from django.contrib import admin

from .models import BackendHealth


@admin.register(BackendHealth)
class BackendHealthAdmin(admin.ModelAdmin):
    date_hierarchy = "time"
    list_display = (
        "plugin_id",
        "backend_type",
        "time",
        "is_healthy",
    )
    readonly_fields = (
        "plugin_id",
        "backend_type",
        "time",
        "is_healthy",
    )
    list_filter = (
        "backend_type",
        "plugin_id",
        "is_healthy",
    )
