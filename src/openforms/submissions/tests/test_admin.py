from unittest.mock import patch

from django.urls import reverse
from django.utils import timezone

from django_webtest import WebTest

from openforms.accounts.tests.factories import UserFactory
from openforms.forms.tests.factories import FormDefinitionFactory, FormStepFactory
from openforms.logging.models import TimelineLogProxy

from ..constants import RegistrationStatuses
from ..models import Submission
from .factories import SubmissionFactory, SubmissionStepFactory


class TestSubmissionAdmin(WebTest):
    @classmethod
    def setUpTestData(cls):
        form_definition = FormDefinitionFactory(
            configuration={
                "components": [
                    {"type": "textfield", "key": "adres"},
                    {"type": "textfield", "key": "voornaam"},
                    {"type": "textfield", "key": "familienaam"},
                    {"type": "date", "key": "geboortedatum"},
                    {"type": "signature", "key": "signature"},
                ]
            }
        )
        step = FormStepFactory.create(form_definition=form_definition)
        cls.submission_1 = SubmissionFactory.create(form=step.form)
        submission_2 = SubmissionFactory.create(
            form=step.form, completed_on=timezone.now()
        )
        cls.submission_step_1 = SubmissionStepFactory.create(
            submission=cls.submission_1,
            form_step=step,
            data={"adres": "Voorburg", "voornaam": "shea", "familienaam": "meyers"},
        )
        SubmissionStepFactory.create(
            submission=submission_2,
            form_step=step,
            data={
                "voornaam": "shea",
                "familienaam": "meyers",
                "geboortedatum": "01-01-1991",
            },
        )

    def setUp(self):
        super().setUp()
        self.user = UserFactory.create(is_superuser=True, is_staff=True, app=self.app)

    def test_displaying_merged_data(self):
        response = self.app.get(
            reverse(
                "admin:submissions_submission_change", args=(self.submission_1.pk,)
            ),
            user=self.user,
        )

        self.assertContains(
            response,
            "<ul><li>adres: Voorburg</li><li>voornaam: shea</li><li>familienaam: meyers</li></ul>",
            html=True,
        )

    def test_displaying_merged_data_displays_signature_as_image(self):
        self.submission_step_1.data["signature"] = "data:image/png;base64,iVBOR"
        self.submission_step_1.save()

        response = self.app.get(
            reverse(
                "admin:submissions_submission_change", args=(self.submission_1.pk,)
            ),
            user=self.user,
        )

        self.assertContains(
            response,
            "<li>signature: <img class='signature-image' src='data:image/png;base64,iVBOR' alt='signature'></li>",
            html=True,
        )

    def test_viewing_submission_details_in_admin_creates_log(self):
        self.app.get(
            reverse(
                "admin:submissions_submission_change", args=(self.submission_1.pk,)
            ),
            user=self.user,
        )

        self.assertEqual(
            TimelineLogProxy.objects.filter(
                template="logging/events/submission_details_view_admin.txt"
            ).count(),
            1,
        )

    def test_export_csv_successfully_exports_csv_file(self):
        response = self.app.get(
            reverse("admin:submissions_submission_changelist"), user=self.user
        )

        form = response.forms["changelist-form"]
        form["action"] = "export_csv"
        form["_selected_action"] = [
            str(submission.pk) for submission in Submission.objects.all()
        ]

        response = form.submit()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["content-type"], "text/csv")
        self.assertEqual(
            response["content-disposition"],
            'attachment; filename="submissions_export.csv"',
        )
        self.assertIsNotNone(response.content)
        self.assertEqual(
            TimelineLogProxy.objects.filter(
                template="logging/events/submission_export_list.txt"
            ).count(),
            1,
        )

    def test_export_xlsx_successfully_exports_xlsx_file(self):
        response = self.app.get(
            reverse("admin:submissions_submission_changelist"), user=self.user
        )

        form = response.forms["changelist-form"]
        form["action"] = "export_xlsx"
        form["_selected_action"] = [
            str(submission.pk) for submission in Submission.objects.all()
        ]

        response = form.submit()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["content-type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        self.assertEqual(
            response["content-disposition"],
            'attachment; filename="submissions_export.xlsx"',
        )
        self.assertIsNotNone(response.content)
        self.assertEqual(
            TimelineLogProxy.objects.filter(
                template="logging/events/submission_export_list.txt"
            ).count(),
            1,
        )

    def test_exporting_multiple_forms_fails(self):
        step = FormStepFactory.create()
        SubmissionFactory.create(form=step.form, completed_on=timezone.now())

        response = self.app.get(
            reverse("admin:submissions_submission_changelist"), user=self.user
        )

        form = response.forms["changelist-form"]
        form["action"] = "export_csv"
        form["_selected_action"] = [
            str(submission.pk) for submission in Submission.objects.all()
        ]

        response = form.submit()

        # Assert redirected back to html page
        self.assertEqual(response.status_code, 302)
        response = response.follow()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["content-type"],
            "text/html; charset=utf-8",
        )
        self.assertFalse(
            TimelineLogProxy.objects.filter(
                template="logging/events/submission_export_list.txt"
            ).exists()
        )

    @patch("openforms.registrations.tasks.retry_register_submission.delay")
    def test_resend_submissions_only_resends_failed_submissions(self, task_mock):
        failed = SubmissionFactory.create(
            registration_status=RegistrationStatuses.failed, completed_on=timezone.now()
        )
        not_failed = SubmissionFactory.create(
            registration_status=RegistrationStatuses.pending,
            completed_on=timezone.now(),
        )

        response = self.app.get(
            reverse("admin:submissions_submission_changelist"), user=self.user
        )

        form = response.forms["changelist-form"]
        form["action"] = "resend_submissions"
        form["_selected_action"] = [str(failed.pk), str(not_failed.pk)]

        form.submit()

        self.assertEqual(task_mock.call_count, 1)
        task_mock.assert_called_once_with(failed.id)
