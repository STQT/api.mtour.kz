from django.core.validators import MinValueValidator, MaxValueValidator, MinLengthValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from ordered_model.models import OrderedModel
from sorl.thumbnail import ImageField

from medtour.contrib.soft_delete_model import SoftDeleteModel
from medtour.tournumbers.instances import get_shots_path


class TourNumbers(OrderedModel, SoftDeleteModel):
    title = models.CharField(max_length=1000, default="1 местн. номера")
    place_count = models.SmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)])
    price = models.IntegerField(verbose_name=_("Цена"))
    holiday_price = models.IntegerField(verbose_name=_("Цена выходного дня"), blank=True, null=True)
    tour = models.ForeignKey("tours.Tour", on_delete=models.CASCADE, related_name='numbers')
    comforts = models.ManyToManyField("tournumbers.NumberComfort", related_name='numbers', blank=True,
                                      verbose_name=_("Удобства"))
    capacity = models.SmallIntegerField(_("Вместимость"), default=1,
                                        validators=[MinValueValidator(1), MaxValueValidator(20)])
    max_capacity = models.SmallIntegerField(_("Макс. Вместимость"), default=1,
                                            validators=[MinValueValidator(1), MaxValueValidator(20)])
    extra_capacity_price = models.IntegerField(_("Цена за доп. место"), default=0)
    hide = models.BooleanField(_("Скрыть"), default=False)
    remarks = models.CharField(_("Примечание"), max_length=1000, default='Примечание', null=True, blank=True)
    order_with_respect_to = "tour"

    class Meta:
        verbose_name = _("* Номер тура")
        verbose_name_plural = _("* Номера туров")

    def __str__(self):
        return self.title


class NumberShots(OrderedModel):
    tour_number = models.ForeignKey("tournumbers.TourNumbers", verbose_name=_("Номер"),
                                    on_delete=models.CASCADE, related_name="number_shots")
    photo = ImageField(_("Изображение"), upload_to=get_shots_path)
    name = models.CharField(_("Имя изображения"), null=True, max_length=50, blank=True)
    order_with_respect_to = "tour_number"

    class Meta:
        verbose_name = _("Изображение номера")
        verbose_name_plural = _("Изображения номера")

    def __str__(self):
        return str(self.order) + "|" + str(self.tour_number.title)


class TourNumbersServices(OrderedModel):
    tour_number = models.ForeignKey("tournumbers.TourNumbers", verbose_name=_("Номера туров"),
                                    related_name="number_services",
                                    help_text=_("Укажите конретный номер тура"), on_delete=models.CASCADE)
    title = models.CharField(_("Услуга включенного номера"), max_length=1000)
    hide = models.BooleanField(_("Скрыть"), default=False)
    order_with_respect_to = "tour_number"

    class Meta:
        verbose_name = _("Услуга номера")
        verbose_name_plural = _("Услуги номера")

    def __str__(self):
        return self.title


class NumberCabinets(SoftDeleteModel):
    tour_number = models.ForeignKey(TourNumbers, on_delete=models.CASCADE, related_name="cabinets",
                                    help_text="Здесь указывается номер тура", verbose_name=_("Номер"))
    number = models.IntegerField(_("Порядковый номер"),
                                 help_text=_("Номер кабинета пакета, присвоится автоматически, "
                                             "при создании пакета"))
    humanize_name = models.CharField(_("Название кабинета"), default=None, null=True, blank=True,
                                     max_length=30, help_text="Наименование номера кабинета вручную")

    def __str__(self):
        return "Номер: {}| Порядковый номер: {}".format(self.tour_number.title, self.number)

    class Meta:
        ordering = ('number',)
        verbose_name = _("Кабинет номера тура")
        verbose_name_plural = _("Кабинеты номера тура")


class NumberComfort(models.Model):
    name = models.CharField(verbose_name=_("Название комфорта"), max_length=100)
    icon = models.FileField(verbose_name=_("Файл иконки"), upload_to="number_icons")

    class Meta:
        verbose_name = _("Название удобства номера")
        verbose_name_plural = _("Название удобств номера")

    def __str__(self):
        return self.name


class NumberReviews(models.Model):
    tour = models.ForeignKey("tournumbers.TourNumbers", on_delete=models.CASCADE, related_name="number_reviews")
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="number_reviews")
    purity = models.IntegerField(_("Чистота"), validators=[MinValueValidator(0), MaxValueValidator(5)], default=0)
    service = models.IntegerField(_("Сервис"), validators=[MinValueValidator(0), MaxValueValidator(5)], default=0)
    location = models.IntegerField(_("Местоположение"), validators=[MinValueValidator(0), MaxValueValidator(5)],
                                   default=0)
    staff = models.IntegerField(_("Персонал"), validators=[MinValueValidator(0), MaxValueValidator(5)], default=0)
    proportion = models.IntegerField(_("Соотношение цена/качество"),
                                     validators=[MinValueValidator(0), MaxValueValidator(5)], default=0)
    text = models.TextField(validators=[
        MinLengthValidator(20, message=_("Минимальная длина отзыва должна превышать 20 символа"))
    ])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user) + ' | ' + str(self.tour)

    class Meta:
        verbose_name = _("Отзыв номера")
        verbose_name_plural = _("Отзывы номеров")
        ordering = ("-created_at",)
