from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ToursConfig(AppConfig):
    name = "medtour.tours"
    verbose_name = _("1. Туры")

    def ready(self):
        import medtour.tours.signals  # noqa
