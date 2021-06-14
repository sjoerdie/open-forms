import logging

from django.conf import settings

from openforms.healthcheck.models import BackendHealth
from openforms.registrations.registry import register as registrations_register

logger = logging.getLogger(__name__)

default_registries = [
    registrations_register,
]

"""
    NOTE

    this is just a rough first version that has never been completed
"""


class BackendHealthCheck:
    registries = default_registries

    def __init__(self, registries=None):
        self.registries = registries or self.registries.copy()

    def get_registries(self):
        return self.registries

    def check_all(self):
        for register in self.get_registries():
            for plugin in register:
                # TODO thread/task
                self.check_plugin(plugin)

    def check_plugin(self, plugin):
        try:
            is_healthy = plugin.check_health()
        except Exception as e:
            logger.exception("error during health check", exc_info=e)
            BackendHealth.objects.update_health(
                plugin.backend_type, plugin.identifier, False
            )
            if settings.DEBUG:
                raise e
        else:
            BackendHealth.objects.update_health(
                plugin.backend_type, plugin.identifier, is_healthy
            )


health_check = BackendHealthCheck()


# TODO register task
def check_plugin_task():
    health_check.check_all()
