from django.utils import timezone

import factory

from ..models import BackendHealth


class BackendHealthFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BackendHealth

    backend_type = "test"
    plugin_id = "test"
    is_healthy = True
    time = factory.LazyFunction(timezone.now)
