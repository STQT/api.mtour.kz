from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator, MinLengthValidator
from django.db import models
from django.db.models import Avg, Count, Func
from django.utils.functional import cached_property
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from multiselectfield import MultiSelectField
from ordered_model.models import OrderedModel
from sorl.thumbnail import get_thumbnail, ImageField

from medtour.contrib.soft_delete_model import SoftDeleteModel
from medtour.tours.instances import get_price_path, get_shots_path
from medtour.users.models import Organization
from medtour.utils import unique_slug_generator
from medtour.utils.constants import CurrencyChoice, WeekDayChoice

User = get_user_model()


class Round(Func):
    function = 'ROUND'
    arity = 2


class Tour(SoftDeleteModel):
    title = models.CharField(max_length=1000, verbose_name=_("Название тура"))
    description = models.TextField(blank=True, null=True, verbose_name=_("Описание"))
    org = models.ForeignKey(Organization, related_name="tours", on_delete=models.SET_NULL,
                            verbose_name=_("Организация"), null=True,
                            help_text=_("Прикрепленная организация к туру"))
    medical_profiles = models.ManyToManyField("tours.TourMedicalProfile", related_name='tours', blank=True)
    currency = models.IntegerField(choices=CurrencyChoice.choices, default=CurrencyChoice.KZT, null=True, blank=True,
                                   verbose_name=_("Валюта"))
    BIN = models.CharField(max_length=16, blank=True, null=True)
    IIK = models.CharField(max_length=50, blank=True, null=True)
    BIK = models.CharField(max_length=15, blank=True, null=True)
    requisites = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("Для предоплаты (IBAN)"))
    address = models.CharField(max_length=1000, blank=True, null=True)
    category = models.ForeignKey("users.OrganizationCategory",
                                 on_delete=models.CASCADE,
                                 verbose_name=_("Категория"),
                                 related_name="tours")

    country = models.ForeignKey("users.Country", verbose_name=_("Страна"), related_name="tour_countries",
                                on_delete=models.SET_NULL, blank=True, null=True)
    region = models.ForeignKey("users.Region", verbose_name=_("Регион"), related_name="tour_regions",
                               on_delete=models.SET_NULL, blank=True, null=True)
    city = models.ForeignKey("users.City", verbose_name=_("Город"), related_name="tour_cities",
                             on_delete=models.SET_NULL, blank=True, null=True)
    slug = models.SlugField(_("Слаг"), blank=True, max_length=255)
    email = models.EmailField(null=True, blank=True, help_text=_("Пожалуйста напишите ваш эмейл"))
    first_name = models.CharField(_("Имя директора"), max_length=100, null=True, blank=True)
    last_name = models.CharField(_("Фамилия директора"), max_length=100, null=True, blank=True)
    district = models.CharField(_("Район"), max_length=255, null=True, blank=True)
    street = models.CharField(_("Улица"), max_length=255, null=True, blank=True)
    home_number = models.CharField(_("Номер дома"), max_length=50, null=True, blank=True)
    youtube_url = models.CharField(_("Ссылка на Youtube"), max_length=1000, null=True, blank=True)
    working_time = models.TextField(_("Время работы"), null=True, blank=True)

    is_top = models.BooleanField(_("Хиты продаж?"), default=False)  # TODO: нужно логику для расчета хитов продаж
    is_moderated = models.BooleanField(default=False, verbose_name=_("Прошел модерацию"), db_index=True)
    is_subscribed = models.BooleanField(_("Подписан?"), default=False, db_index=True,
                                        help_text=_("Отметьте, если он подписан"))
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    __original_title = None

    class Meta:
        verbose_name = _("* Тур")
        verbose_name_plural = _("* Туры")
        ordering = ['-created_at']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_title = self.title

    def __str__(self):
        return self.title if self.title else _("Нет имени")

    def save(self, *args, **kwargs):
        if not self.slug:  # noqa
            self.slug = unique_slug_generator(self, self.title)
        if self.title != self.__original_title:
            self.slug = unique_slug_generator(self, self.title)
        super().save(*args, **kwargs)
        self.__original_title = self.title

    @cached_property
    def average_rating(self):
        return self.comments.aggregate(
            service__avg=Round(Avg('service'), 2, output_field=models.FloatField()),
            location__avg=Round(Avg('location'), 2, output_field=models.FloatField()),
            purity__avg=Round(Avg('purity'), 2, output_field=models.FloatField()),
            staff__avg=Round(Avg('staff'), 2, output_field=models.FloatField()),
            proportion__avg=Round(Avg('proportion'), 2, output_field=models.FloatField()),
            comments__count=Count('purity', output_field=models.FloatField())
        )


class TourPhones(models.Model):
    tour = models.ForeignKey(Tour, related_name="tour_phones", on_delete=models.CASCADE,
                             verbose_name=_("Тур"))
    phone = models.CharField(max_length=50, verbose_name=_("Телефонный номер"))

    class Meta:
        verbose_name = _("Телефонный номер тура")
        verbose_name_plural = _("Телефонные номера тура")


class TourShots(OrderedModel):
    name = models.CharField(_("Имя изображения"), null=True, max_length=1000, blank=True)
    tour = models.ForeignKey(Tour, related_name="tour_shots", on_delete=models.CASCADE,
                             verbose_name=_("Изображения тура"),
                             help_text=_("Прикрепленный тур"))
    photo = ImageField(_("Изображение"),
                       upload_to=get_shots_path)
    order_with_respect_to = "tour"

    class Meta:
        verbose_name = _("Изображения тура")
        verbose_name_plural = _("Изображения туров")

    def __str__(self):
        return str(self.name) + "|" + str(self.order)

    @property
    def thumbnail_preview(self):
        if self.photo:
            _thumbnail = get_thumbnail(self.photo, '50x50', upscale=False, crop="center", quality=100)
            return format_html(
                '<img src="{}" width="{}" height="{}">'.format(_thumbnail.url, _thumbnail.width, _thumbnail.height))
        return ""


class TourPriceFile(models.Model):
    tour = models.OneToOneField(Tour, on_delete=models.CASCADE,
                                related_name='price_file')
    file = models.FileField(upload_to=get_price_path)

    def __str__(self):
        return str(self.tour.title)


class TourLocation(models.Model):
    """Локация тура должна быть только один у тура"""
    tour = models.OneToOneField(Tour, related_name="location", on_delete=models.CASCADE)
    lon = models.FloatField(null=True, blank=True, verbose_name=_("Долгота"))
    lat = models.FloatField(null=True, blank=True, verbose_name=_("Широта"))

    class Meta:
        verbose_name = _("Локация тура")
        verbose_name_plural = _("Локации тура")

    def __str__(self):
        return str(self.tour.title)


class AdditionalTitles(models.Model):
    name = models.CharField(max_length=1000)
    tour = models.ForeignKey(Tour, null=True, blank=True, on_delete=models.SET_NULL,
                             related_name='tour_titles')

    class Meta:
        verbose_name = _("Готовая заголовка доп. услуги")
        verbose_name_plural = _("Готовые заголовки доп. услуг")

    def __str__(self):
        return self.name


class TourAdditionalTitle(models.Model):
    """
    Таблица для дополнительных заголовков,
    которых выбрал тур.
    Здесь может он выбрать либо создать заголовок.
    Если выберет готовый, то указывается уже имеющийся
    AdditionalTitles объект, если нет подходящего заголовка,
    то пересоздается новый AdditionalTitles объект.
    """
    tour = models.ForeignKey(Tour, related_name="additional_titles", on_delete=models.CASCADE)
    title = models.ForeignKey("tours.AdditionalTitles", on_delete=models.CASCADE,
                              related_name="additional_titles")

    class Meta:
        verbose_name = _("* Заголовка бесплатных услуг")
        verbose_name_plural = _("* Заголовки бесплатных услуг")

    def __str__(self):
        return self.title.name


class AdditionalInfoServices(models.Model):
    title = models.ForeignKey(TourAdditionalTitle, on_delete=models.CASCADE, related_name="additional_services")
    service = models.CharField(max_length=1000, verbose_name="Наименование услуги")

    class Meta:
        verbose_name = _("Бесплатная услуга")
        verbose_name_plural = _("Бесплатные услуги тура")

    def __str__(self):
        return self.service


class TourPaidServices(OrderedModel):
    name = models.CharField(_("Название услуги"), max_length=1000,
                            help_text=_("Наименование платной услуги"))
    description = models.TextField(_("Описание услуги"), blank=True, null=True,
                                   help_text=_("Описание конкретной услуги"))
    price = models.IntegerField(_("Стоимость услуги"),
                                help_text=_("Стоимость платной услуги"))
    tour = models.ForeignKey(Tour, verbose_name=_("Прикрепленный тур"),
                             related_name="services", on_delete=models.CASCADE,
                             help_text=_("Прикрепленный тур"))
    hide = models.BooleanField(_("Скрыть"), default=False)

    class Meta:
        verbose_name = _("* Платная услуга тура")
        verbose_name_plural = _("* Платные услуги тура")

    def __str__(self):
        return self.name


class CommentTour(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
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
        verbose_name = _("Отзыв тура")
        verbose_name_plural = _("Отзывы тура")
        ordering = ("-created_at",)


class TourBookingWeekDays(models.Model):
    tour = models.OneToOneField(Tour, on_delete=models.CASCADE)
    days = MultiSelectField(choices=WeekDayChoice.choices,
                            default=WeekDayChoice.WEDNESDAY,
                            max_choices=10)

    class Meta:
        verbose_name = _("День бронирования тура")
        verbose_name_plural = _("Дни бронирований тура")

    def __str__(self):
        return str(self.tour.title)


class TourBookingHoliday(models.Model):
    tour = models.OneToOneField(Tour, on_delete=models.CASCADE, related_name="holiday")  # noqa
    days = MultiSelectField(choices=WeekDayChoice.choices,
                            default=[WeekDayChoice.SATURDAY, WeekDayChoice.YESTERDAY],
                            max_choices=7)

    class Meta:
        verbose_name = _("Выходные дни тура")
        verbose_name_plural = _("Выходные дни тура")

    def __str__(self):
        return str(self.tour.title)


class TourBookingExtraHolidays(models.Model):
    tour = models.ForeignKey("tours.Tour", on_delete=models.CASCADE,
                             related_name="extra_days")  # noqa
    date = models.DateField(_("День года"))

    class Meta:
        verbose_name = _("Выходные дополнительные дни тура")
        verbose_name_plural = _("Выходные дополнительные дни тура")

    def __str__(self):
        return str(self.tour.title)


class TourMedicalProfile(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name = _("Медицинский профиль")
        verbose_name_plural = _("Медицинские профили")

    def __str__(self):
        return self.name
