from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class TournumbersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'medtour.tournumbers'
    verbose_name = _("Номера туров")

    def ready(self):
        import medtour.tournumbers.signals  # noqa
