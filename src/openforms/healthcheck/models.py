import logging

from django.db import models, transaction
from django.utils.translation import ugettext_lazy as _

from openforms.healthcheck.constants import BackendType

logger = logging.getLogger(__name__)


class BackendHealthQuerySet(models.QuerySet):
    def filter_for(self, backend_type: str, plugin_id: str):
        return self.filter(backend_type=backend_type, plugin_id=plugin_id)

    def get_last_for(self, backend_type: str, plugin_id: str):
        return self.filter_for(backend_type, plugin_id).last()

    def is_healthy(self, backend_type: str, plugin_id: str) -> bool:
        return (
            self.filter_for(backend_type, plugin_id)
            .values_list("is_healthy", flat=True)
            .last()
            or False
        )


class BackendHealthManager(models.Manager.from_queryset(BackendHealthQuerySet)):
    def update_health(
        self, backend_type: str, plugin_id: str, is_healthy: bool
    ) -> bool:
        with transaction.atomic():
            obj = self.select_for_update().get_last_for(backend_type, plugin_id)

            if not obj or obj.is_healthy != is_healthy:
                self.create(
                    backend_type=backend_type,
                    plugin_id=plugin_id,
                    is_healthy=is_healthy,
                )
                logger.info(
                    f"backend '{backend_type}' plugin '{plugin_id}' health changed to '{BackendHealth.get_label(is_healthy)}"
                )
                return True
            else:
                return False


class BackendHealth(models.Model):
    backend_type = models.CharField(
        _("backend type"), choices=BackendType.choices, max_length=32
    )
    plugin_id = models.CharField(_("plugin id"), max_length=255)

    time = models.DateTimeField(_("time"), auto_now_add=True)
    is_healthy = models.BooleanField(_("healthy"))

    objects = BackendHealthManager()

    class Meta:
        verbose_name = _("Health Check")
        # NOTE we explicitly DO NOT order by 'time'
        #  because we just want the last record in the database and no system clock problems or race-conditions
        ordering = ("pk",)
        # TODO check indexes

    def get_health_label(self):
        return BackendHealth.get_label(self.is_healthy)

    @staticmethod
    def get_label(is_healthy):
        if is_healthy:
            return _("healthy")
        else:
            return _("unhealthy")

    def __str__(self):
        return f"{self.backend_type}.{self.plugin_id}"
