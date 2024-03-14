from django.core.validators import MinValueValidator, MaxValueValidator, MinLengthValidator
from django.db import models
from django.db.models import Avg, Count, Func
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from ordered_model.models import OrderedModel
from sorl.thumbnail import get_thumbnail, ImageField

from medtour.contrib.soft_delete_model import SoftDeleteModel
from medtour.guides.instances import get_shots_path, get_program_path
from medtour.utils import unique_slug_generator
from medtour.utils.constants import CurrencyChoice, GuideComplexityChoice, GuideDurationTypeChoice


class Round(Func):
    function = 'ROUND'
    arity = 2


class GuideCategory(models.Model):  # noqa
    title = models.CharField(_("Title"), max_length=100)  # noqa
    slug = models.SlugField(_("Слаг"), blank=True, max_length=255)
    photo = models.ImageField(default='/static/images/default.svg', upload_to="banners")
    icon = models.ImageField(default='/static/images/cart.svg', upload_to="category_icons")
    icon_active = models.ImageField(default='/static/images/cart.svg', upload_to="category_icons")
    title_color = models.CharField(default='#FFFFFF', max_length=10)
    column = models.CharField(default="two", max_length=10)

    class Meta:
        verbose_name = _("Категория гида")
        verbose_name_plural = _("Категории гидов")
        ordering = ("title",)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = unique_slug_generator(self, self.title)
        super().save(*args, **kwargs)


class Guide(SoftDeleteModel):
    title = models.CharField(max_length=100, verbose_name=_("Название гида"))
    description = models.TextField(blank=True, null=True, verbose_name=_("Общая информация"))
    org = models.OneToOneField("users.Organization", related_name="guides", on_delete=models.SET_NULL,
                               verbose_name=_("Организация"), null=True,
                               help_text=_("Прикрепленная организация к гиду"))
    category = models.ForeignKey("guides.GuideCategory",
                                 on_delete=models.PROTECT,
                                 verbose_name=_("Категория"),
                                 related_name="guides")
    currency = models.IntegerField(choices=CurrencyChoice.choices, default=CurrencyChoice.KZT, null=True, blank=True,
                                   verbose_name=_("Валюта"))
    BIN = models.CharField(max_length=16, blank=True, null=True)
    IIK = models.CharField(max_length=50, blank=True, null=True)
    BIK = models.CharField(max_length=15, blank=True, null=True)
    requisites = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("Для предоплаты (IBAN)"))

    country = models.ForeignKey("users.Country", verbose_name=_("Страна"), related_name="guide_countries",
                                on_delete=models.SET_NULL, blank=True, null=True)
    region = models.ForeignKey("users.Region", verbose_name=_("Регион"), related_name="guide_regions",
                               on_delete=models.SET_NULL, blank=True, null=True)
    city = models.ForeignKey("users.City", verbose_name=_("Город"), related_name="guide_cities",
                             on_delete=models.SET_NULL, blank=True, null=True)
    email = models.EmailField(null=True, blank=True, help_text=_("Пожалуйста напишите ваш эмейл"))
    address = models.CharField(_("Адрес организации"), max_length=255, null=True, blank=True)
    working_time = models.TextField(_("Время работы"), null=True, blank=True)
    youtube_url = models.CharField(_("Ссылка на Youtube"), max_length=200, null=True, blank=True)
    lon = models.FloatField(_("Долгота адреса"), blank=True, null=True)
    lat = models.FloatField(_("Широта адреса"), blank=True, null=True)
    slug = models.SlugField(_("Слаг"), blank=True, max_length=255)

    is_top = models.BooleanField(_("Хиты продаж?"), default=False)  # TODO: нужно логику для расчета хитов продаж
    is_moderated = models.BooleanField(default=False, verbose_name=_("Прошел модерацию"), db_index=True)
    is_subscribed = models.BooleanField(_("Подписан?"), default=False, db_index=True,
                                        help_text=_("Отметьте, если он подписан"))
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    __original_title = None

    class Meta:
        verbose_name = _("Гид")
        verbose_name_plural = _("Гиды")
        ordering = ['-created_at']

    def __str__(self):
        return self.title if self.title else _("Нет имени")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_title = self.title

    def save(self, *args, **kwargs):
        if not self.slug:  # noqa
            self.slug = unique_slug_generator(self, self.title)
        if self.title != self.__original_title:
            self.slug = unique_slug_generator(self, self.title)
        super().save(*args, **kwargs)
        self.__original_title = self.title

    @property
    def average_rating(self):
        return self.guide_reviews.aggregate(
            service__avg=Round(Avg('service'), 2, output_field=models.FloatField()),
            location__avg=Round(Avg('location'), 2, output_field=models.FloatField()),
            staff__avg=Round(Avg('staff'), 2, output_field=models.FloatField()),
            proportion__avg=Round(Avg('proportion'), 2, output_field=models.FloatField()),
            reviews__count=Count('service', output_field=models.FloatField())
        )


class GuideReview(models.Model):
    guide = models.ForeignKey(Guide, on_delete=models.CASCADE, related_name="guide_reviews")
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name="guide_reviews")
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
        return str(self.user) + ' | ' + str(self.guide)

    class Meta:
        verbose_name = _("Отзыв тура")
        verbose_name_plural = _("Отзывы тура")
        ordering = ("-created_at",)


class GuideShots(OrderedModel):
    name = models.CharField(_("Имя изображения"), null=True, max_length=50, blank=True)
    guide = models.ForeignKey(Guide, related_name="guide_shots", on_delete=models.CASCADE,
                              verbose_name=_("Гид"),
                              help_text=_("Прикрепленный гид"))
    photo = ImageField(_("Изображение"),
                       upload_to=get_shots_path)
    order_with_respect_to = "guide"

    class Meta:
        verbose_name = _("Изображение гида")
        verbose_name_plural = _("Изображения гидов")

    def __str__(self):
        return str(self.name) + "|" + str(self.order)

    @property
    def thumbnail_preview(self):
        if self.photo:
            _thumbnail = get_thumbnail(self.photo, '300x350', upscale=False, crop="center", quality=100)
            return format_html(
                '<img src="{}" width="{}" height="{}">'.format(_thumbnail.url, _thumbnail.width, _thumbnail.height))
        return ""


class GuideProgram(OrderedModel, SoftDeleteModel):
    name = models.CharField(_("Название программы"), max_length=255)
    guide = models.ForeignKey(Guide, on_delete=models.CASCADE, related_name='programs')
    photo = ImageField(_("Изображение программы"), upload_to=get_program_path, null=True, blank=True)
    description = models.TextField(verbose_name=_("Описание программы"))
    program = models.TextField(verbose_name=_("Программа"))
    price = models.IntegerField(verbose_name=_("Цена"))
    venue_lon = models.FloatField(_("Долгота места встречи"))
    venue_lat = models.FloatField(_("Широта места встречи"))
    venue_address = models.CharField(_("Адрес места встречи"), max_length=200)
    hide = models.BooleanField(_("Скрыть"), default=False)
    complexity = models.CharField(_("Сложность"), max_length=10,
                                  choices=GuideComplexityChoice.choices, default=GuideComplexityChoice.EASY)
    duration = models.SmallIntegerField(default=0)
    duration_type = models.CharField(_("Тип времени продолжительности"), max_length=10,
                                     choices=GuideDurationTypeChoice.choices, default=GuideDurationTypeChoice.MINUTES)
    seats_count = models.IntegerField(_("Количество мест"), default=0)
    services = models.ManyToManyField("guides.GuideServices", verbose_name=_("Включенные услуги"), blank=True)
    remarks = models.CharField(_("Примечание"), max_length=50, default='Примечание', null=True, blank=True)
    order_with_respect_to = "guide"

    class Meta:
        verbose_name = _("Программа гида")
        verbose_name_plural = _("Программы гидов")

    def __str__(self):
        return "Гид: {} | Програма: {}".format(self.guide.title, self.name)


class GuideServices(models.Model):
    title = models.CharField(_("Название услуги"), max_length=50)
    guide = models.ForeignKey(Guide, verbose_name=_("Гид"),
                              on_delete=models.CASCADE, related_name="guide_services")

    class Meta:
        verbose_name = _("Услуга гида")
        verbose_name_plural = _("Услуги гида")

    def __str__(self):
        return self.title
