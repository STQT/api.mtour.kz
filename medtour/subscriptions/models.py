from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

from medtour.tours.models import Tour


class SubscribePrice(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Название пакета"))
    price = models.IntegerField(verbose_name=_("Цена"))
    created_at = models.DateTimeField(auto_now_add=True)
    numbers_of_months = models.SmallIntegerField(default=3, validators=[MinValueValidator(1), MaxValueValidator(24)])
    is_actual = models.BooleanField(default=True, verbose_name=_("Актуален ли?"))

    class Meta:
        verbose_name = _("Стоимость подписки")
        verbose_name_plural = _("Стоимость подписок")

    def __str__(self):
        return self.name


class TourSubscribe(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, db_index=True)
    subscribe_price = models.ForeignKey(SubscribePrice, on_delete=models.PROTECT, verbose_name=_("Тип подписки"))
    created_at = models.DateField(auto_now_add=True)
    overdue = models.BooleanField(default=False)
    payment_receipt = models.CharField(max_length=255, null=True, blank=True)
    is_paid = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("Подписка тура")
        verbose_name_plural = _("Подписки туров")


class SubscribeQueue(models.Model):
    subscribe = models.ForeignKey(TourSubscribe, on_delete=models.CASCADE)
    processed = models.BooleanField(default=False, db_index=True)
