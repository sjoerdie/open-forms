from django.contrib import admin, messages
from django.contrib.contenttypes.admin import GenericTabularInline
from django.template.defaultfilters import filesizeformat
from django.utils.translation import gettext_lazy as _, ngettext

from privates.admin import PrivateMediaMixin
from privates.views import PrivateMediaView

from openforms.appointments.models import AppointmentInfo
from openforms.logging.logevent import (
    submission_details_view_admin,
    submission_export_list as log_export_submissions,
)
from openforms.logging.models import TimelineLogProxy
from openforms.payments.models import SubmissionPayment
from openforms.registrations.tasks import retry_register_submission

from .constants import IMAGE_COMPONENTS, RegistrationStatuses
from .exports import export_submissions
from .models import (
    Submission,
    SubmissionFileAttachment,
    SubmissionReport,
    SubmissionStep,
    TemporaryFileUpload,
)


class SubmissionTypeListFilter(admin.ListFilter):
    title = _("type")
    parameter_name = "type"

    def __init__(self, request, params, model, model_admin):
        super().__init__(request, params, model, model_admin)

        self.request = request

        if self.parameter_name in params:
            value = params.pop(self.parameter_name)
            self.used_parameters[self.parameter_name] = value

    def show_all(self):
        return self.used_parameters.get(self.parameter_name) == "__all__"

    def has_output(self):
        """
        This needs to return ``True`` to work.
        """
        return True

    def choices(self, changelist):
        result = [
            {
                "selected": self.show_all(),
                "query_string": changelist.get_query_string(
                    {self.parameter_name: "__all__"}
                ),
                "display": _("All"),
            },
            {
                "selected": not self.show_all(),
                "query_string": changelist.get_query_string(
                    remove=[self.parameter_name]
                ),
                "display": _("Submissions"),
            },
        ]
        return result

    def queryset(self, request, queryset):
        if not self.show_all():
            return queryset.exclude(completed_on=None)

    def expected_parameters(self):
        return [self.parameter_name]


class SubmissionStepInline(admin.StackedInline):
    model = SubmissionStep
    extra = 0
    fields = (
        "uuid",
        "form_step",
        "data",
    )


class SubmissionPaymentInline(admin.StackedInline):
    model = SubmissionPayment
    extra = 0
    fields = (
        "uuid",
        "created",
        "submission",
        "plugin_id",
        "form_url",
        "order_id_str",
        "amount",
        "status",
    )
    readonly_fields = fields

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def order_id_str(self, obj):
        # property to stop Django localising the integer
        return str(obj.order_id)

    order_id_str.short_description = _("Order ID")
    order_id_str.admin_order_field = "order_id"


class SubmissionLogInline(GenericTabularInline):
    model = TimelineLogProxy
    fields = ("get_message",)
    readonly_fields = ("get_message",)
    template = "logging/admin_inline.html"

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    date_hierarchy = "completed_on"
    list_display = (
        "form",
        "registration_status",
        "last_register_date",
        "created_on",
        "completed_on",
    )
    list_filter = ("form", SubmissionTypeListFilter)
    search_fields = ("form__name",)
    inlines = [
        SubmissionStepInline,
        SubmissionPaymentInline,
        SubmissionLogInline,
    ]
    readonly_fields = [
        "created_on",
        "get_registration_backend",
        "get_appointment_status",
        "get_appointment_id",
        "get_appointment_error_information",
        "on_completion_task_ids",
        "confirmation_email_sent",
    ]
    actions = ["export_csv", "export_xlsx", "resend_submissions"]

    def get_registration_backend(self, obj):
        return obj.form.registration_backend

    get_registration_backend.short_description = _("Registration backend")

    def get_appointment_status(self, obj):
        try:
            return obj.appointment_info.status
        except AppointmentInfo.DoesNotExist:
            return ""

    get_appointment_status.short_description = _("Appointment status")

    def get_appointment_id(self, obj):
        try:
            return obj.appointment_info.appointment_id
        except AppointmentInfo.DoesNotExist:
            return ""

    get_appointment_id.short_description = _("Appointment Id")

    def get_appointment_error_information(self, obj):
        try:
            return obj.appointment_info.error_information
        except AppointmentInfo.DoesNotExist:
            return ""

    get_appointment_error_information.short_description = _(
        "Appointment error information"
    )

    def change_view(self, request, object_id, form_url="", extra_context=None):
        submission = self.get_object(request, object_id)
        submission_details_view_admin(submission, request.user)
        extra_context = {
            "data": submission.get_ordered_data_with_component_type(),
            "attachments": submission.get_merged_attachments(),
            "image_components": IMAGE_COMPONENTS,
        }
        return super().change_view(
            request,
            object_id,
            form_url=form_url,
            extra_context=extra_context,
        )

    def _export(self, request, queryset, file_type):
        if queryset.order_by().values("form").distinct().count() > 1:
            messages.error(
                request,
                _("You can only export the submissions of the same form type."),
            )
            return

        log_export_submissions(queryset.first().form, request.user)
        return export_submissions(queryset, file_type)

    def export_csv(self, request, queryset):
        return self._export(request, queryset, "csv")

    export_csv.short_description = _(
        "Export selected %(verbose_name_plural)s as CSV-file."
    )

    def export_xlsx(self, request, queryset):
        return self._export(request, queryset, "xlsx")

    export_xlsx.short_description = _(
        "Export selected %(verbose_name_plural)s as Excel-file."
    )

    def resend_submissions(self, request, queryset):
        submissions = queryset.filter(registration_status=RegistrationStatuses.failed)
        messages.success(
            request,
            ngettext(
                "Resending {count} {verbose_name} to registration backend",
                "Resending {count} {verbose_name_plural} to registration backend",
                submissions.count(),
            ).format(
                count=submissions.count(),
                verbose_name=queryset.model._meta.verbose_name,
                verbose_name_plural=queryset.model._meta.verbose_name_plural,
            ),
        )
        for submission in submissions:
            retry_register_submission.delay(submission.id)

    resend_submissions.short_description = _(
        "Resend %(verbose_name_plural)s to the registration backend."
    )


@admin.register(SubmissionReport)
class SubmissionReportAdmin(PrivateMediaMixin, admin.ModelAdmin):
    list_display = ("title",)
    list_filter = ("title",)
    search_fields = ("title",)
    raw_id_fields = ("submission",)

    private_media_fields = ("content",)

    def has_add_permission(self, request, obj=None):
        return False


class TemporaryFileUploadMediaView(PrivateMediaView):
    def get_sendfile_opts(self):
        object = self.get_object()
        return {
            "attachment": True,
            "attachment_filename": object.file_name,
            "mimetype": object.content_type,
        }


@admin.register(TemporaryFileUpload)
class TemporaryFileUploadAdmin(PrivateMediaMixin, admin.ModelAdmin):
    list_display = (
        "uuid",
        "file_name",
        "content_type",
        "created_on",
        "file_size",
    )
    fields = (
        "uuid",
        "created_on",
        "file_name",
        "content_type",
        "file_size",
        "content",
    )

    search_fields = ("uuid",)
    readonly_fields = (
        "uuid",
        "created_on",
        "file_size",
    )
    date_hierarchy = "created_on"

    private_media_fields = ("content",)
    private_media_view_class = TemporaryFileUploadMediaView

    def file_size(self, obj):
        return filesizeformat(obj.content.size)

    file_size.short_description = _("File size")

    def has_add_permission(self, request, obj=None):
        return False


class SubmissionFileAttachmentMediaView(PrivateMediaView):
    def get_sendfile_opts(self):
        object = self.get_object()
        return {
            "attachment": True,
            "attachment_filename": object.get_display_name(),
            "mimetype": object.content_type,
        }


@admin.register(SubmissionFileAttachment)
class SubmissionFileAttachmentAdmin(PrivateMediaMixin, admin.ModelAdmin):
    list_display = (
        "uuid",
        "file_name",
        "content_type",
        "created_on",
        "file_size",
    )
    fields = (
        "uuid",
        "submission_step",
        "form_key",
        "created_on",
        "original_name",
        "content_type",
        "file_size",
        "content",
    )
    raw_id_fields = ("submission_step",)
    readonly_fields = (
        "uuid",
        "created_on",
        "file_size",
    )
    date_hierarchy = "created_on"

    private_media_fields = ("content",)
    private_media_view_class = SubmissionFileAttachmentMediaView

    def file_size(self, obj):
        return filesizeformat(obj.content.size)

    file_size.short_description = _("File size")

    def has_add_permission(self, request, obj=None):
        return False
