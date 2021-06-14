from django.utils.translation import ugettext_lazy as _

from djchoices import ChoiceItem, DjangoChoices


class BackendType(DjangoChoices):
    registration = ChoiceItem("registration", _("registration"))
    prefill = ChoiceItem("prefill", _("prefill"))
    authentication = ChoiceItem("authentication", _("authentication"))
