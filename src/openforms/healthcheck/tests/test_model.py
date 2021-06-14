from django.test import TestCase
from django.utils.translation import ugettext as _

from openforms.healthcheck.models import BackendHealth
from openforms.healthcheck.tests.factories import BackendHealthFactory


class BackendHealthCheckTestCase(TestCase):
    def test_model(self):
        health = BackendHealthFactory(is_healthy=True)
        self.assertEqual(str(health), "test.test")
        self.assertEqual(health.get_health_label(), _("healthy"))
        self.assertEqual(BackendHealth.get_label(True), _("healthy"))
        self.assertEqual(BackendHealth.get_label(False), _("unhealthy"))

    def test_queryset_filter_for(self):
        one = BackendHealthFactory(backend_type="foo", plugin_id="bar")
        two = BackendHealthFactory(backend_type="buzz", plugin_id="bazz")

        res = list(BackendHealth.objects.filter_for("foo", "bar"))
        self.assertEqual(res, [one])

        res = list(BackendHealth.objects.filter_for("foo", "bazz"))
        self.assertEqual(res, [])

    def test_queryset_get_last_for(self):
        # no record
        res = BackendHealth.objects.get_last_for("test", "test")
        self.assertEqual(res, None)

        # some records
        one = BackendHealthFactory(is_healthy=False)
        two = BackendHealthFactory(is_healthy=False)
        res = BackendHealth.objects.get_last_for("test", "test")
        self.assertEqual(res, two)

        three = BackendHealthFactory(is_healthy=True)
        res = BackendHealth.objects.get_last_for("test", "test")
        self.assertEqual(res, three)

    def test_queryset_is_healthy(self):
        self.assertEqual(BackendHealth.objects.is_healthy("test", "test"), False)

        BackendHealthFactory(is_healthy=True)
        self.assertEqual(BackendHealth.objects.is_healthy("test", "test"), True)

        BackendHealthFactory(is_healthy=False)
        self.assertEqual(BackendHealth.objects.is_healthy("test", "test"), False)

    def test_queryset_update_health(self):
        # healthy
        changed = BackendHealth.objects.update_health("test", "test", True)
        self.assertEqual(changed, True)
        self.assertEqual(BackendHealth.objects.count(), 1)
        self.assertEqual(BackendHealth.objects.last().is_healthy, True)

        # still healthy, no change
        changed = BackendHealth.objects.update_health("test", "test", True)
        self.assertEqual(changed, False)
        self.assertEqual(BackendHealth.objects.count(), 1)
        self.assertEqual(BackendHealth.objects.last().is_healthy, True)

        # unhealthy
        changed = BackendHealth.objects.update_health("test", "test", False)
        self.assertEqual(changed, True)
        self.assertEqual(BackendHealth.objects.count(), 2)
        self.assertEqual(BackendHealth.objects.last().is_healthy, False)

        # still unhealthy, no change
        changed = BackendHealth.objects.update_health("test", "test", False)
        self.assertEqual(changed, False)
        self.assertEqual(BackendHealth.objects.count(), 2)
        self.assertEqual(BackendHealth.objects.last().is_healthy, False)
