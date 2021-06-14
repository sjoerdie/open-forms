from django.apps import AppConfig


class HealthCheckConfig(AppConfig):
    name = "openforms.healthcheck"
    verbose_name = "Health check"

    def ready(self):
        pass
