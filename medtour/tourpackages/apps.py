from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class TourpackagesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'medtour.tourpackages'
    verbose_name = _("Пакеты туров")
