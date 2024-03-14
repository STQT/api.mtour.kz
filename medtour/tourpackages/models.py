from django.db import models
from django.utils.translation import gettext_lazy as _
from ordered_model.models import OrderedModel

from medtour.contrib.soft_delete_model import SoftDeleteModel


class TourPackages(OrderedModel, SoftDeleteModel):
    title = models.CharField(_("Название пакета"), max_length=1000,
                             help_text="Примерное наименование: Комфорт, Стандарт, Номер на 1 человек")
    tour = models.ForeignKey("tours.Tour", related_name="packages", on_delete=models.CASCADE,
                             verbose_name=_("Тур"),
                             help_text=_("Указывайте для прикрепления к туру"))
    number = models.ForeignKey("tournumbers.TourNumbers", on_delete=models.CASCADE,
                               verbose_name=_("Номер пакета"),
                               help_text=_("Укажите сколько местный кабинет в туре"),
                               related_name="packages")
    price = models.IntegerField(verbose_name=_("Цена"))
    holiday_price = models.IntegerField(verbose_name=_("Цена выходного дня"), blank=True, null=True)
    hide = models.BooleanField(_("Скрыть"), default=False)
    remarks = models.CharField(_("Примечание"), max_length=1000, default='Примечание', null=True, blank=True)
    order_with_respect_to = "tour"

    class Meta:
        verbose_name = _("* Тур пакет")
        verbose_name_plural = _("* Тур пакеты")

    def __str__(self):
        return self.title


class TourPackagesServices(models.Model):
    package = models.ForeignKey(TourPackages, related_name="package_services", on_delete=models.CASCADE)
    title = models.CharField(max_length=1000, verbose_name=_("Услуга сервиса"))
    hide = models.BooleanField(default=False, verbose_name=_("Скрыть"))

    class Meta:
        verbose_name = _("Услуга пакета")
        verbose_name_plural = _("Услуги пакета")

    def __str__(self):
        return self.title
