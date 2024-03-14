from django.core.validators import MinValueValidator, MaxValueValidator, MinLengthValidator
from django.db import models
from django.db.models import Func
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from multiselectfield import MultiSelectField
from ordered_model.models import OrderedModel
from sorl.thumbnail import get_thumbnail, ImageField

from medtour.contrib.soft_delete_model import SoftDeleteModel
from medtour.guides.instances import get_program_path
from medtour.utils import unique_slug_generator
from medtour.utils.constants import (
    GuideComplexityChoice, GuideDurationTypeChoice, DistanceUnitChoice,
    LanguagesChoice, ProgramTypeChoices, BackpackWeightChoice, PriceTypeChoices)


class Round(Func):
    function = 'ROUND'
    arity = 2


class GuideCategory(models.Model):  # noqa
    title = models.CharField(_("Title"), max_length=100)  # noqa
    slug = models.SlugField(_("Слаг"), blank=True, max_length=255)
    photo = models.ImageField(default='/static/images/default.svg', upload_to="banners")
    icon = models.FileField(default='/static/images/cart.svg', upload_to="category_icons")
    title_color = models.CharField(default='#FFFFFF', max_length=10)
    column = models.CharField(default="two", max_length=10)
    is_main = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("Категория гида")
        verbose_name_plural = _("Категории гидов")
        ordering = ("title",)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = unique_slug_generator(self, self.title)
        super().save(*args, **kwargs)


class ProgramPrice(models.Model):
    program = models.ForeignKey("guides.Program", related_name="program_prices", on_delete=models.CASCADE)
    price_type = models.CharField(max_length=10, choices=PriceTypeChoices.choices, default=PriceTypeChoices.ALL)
    is_main = models.BooleanField(default=False)
    cost = models.IntegerField()


class Program(OrderedModel, SoftDeleteModel):
    name = models.CharField(_("Название программы"), max_length=255)
    tour = models.ForeignKey("tours.Tour", on_delete=models.CASCADE, related_name='programs')
    type = models.CharField(_("Тип программы"), max_length=10, choices=ProgramTypeChoices.choices)
    venue_lon = models.FloatField(_("Долгота места встречи"))
    venue_lat = models.FloatField(_("Широта места встречи"))
    venue_address = models.CharField(_("Адрес места встречи"), max_length=200)
    hide = models.BooleanField(_("Скрыть"), default=False)
    complexity = models.CharField(_("Сложность"), max_length=10,
                                  choices=GuideComplexityChoice.choices)
    duration = models.SmallIntegerField()
    duration_type = models.CharField(_("Тип времени продолжительности"), max_length=10,
                                     choices=GuideDurationTypeChoice.choices)
    backpack_weight = models.CharField(_("Вес рюкзака"), max_length=10, choices=BackpackWeightChoice.choices)
    seats_count = models.IntegerField(_("Количество мест"))
    services = models.ManyToManyField("guides.ProgramServices", verbose_name=_("Включенные услуги"), blank=True,
                                      related_name="program_services")
    excluded_services = models.ManyToManyField("guides.ProgramServices",
                                               verbose_name=_("Не включенные услуги"),
                                               blank=True, related_name="program_excluded_services")
    remarks = models.CharField(_("Примечание"), max_length=50, default='Примечание', null=True, blank=True)

    children_age = models.SmallIntegerField(_("Возраст детей"))
    distance = models.SmallIntegerField(_("Дистанция"))
    distance_unit = models.CharField(_("Единица измерения дистанции"),
                                     choices=DistanceUnitChoice.choices, max_length=2)
    languages = MultiSelectField(choices=LanguagesChoice.choices, max_choices=5)
    completion_site = models.CharField(_("Место встречи"), max_length=100)

    order_with_respect_to = "tour"

    class Meta:
        verbose_name = _("Программа гида")
        verbose_name_plural = _("Программы гидов")

    def __str__(self):
        return "Гид: {} | Програма: {}".format(self.tour.title, self.name)


class ProgramReview(models.Model):
    program = models.ForeignKey("guides.Program", on_delete=models.CASCADE, related_name="program_reviews")
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name="program_reviews")
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
        return str(self.user) + ' | ' + str(self.program)

    class Meta:
        verbose_name = _("Отзыв программы")
        verbose_name_plural = _("Отзывы программы")
        ordering = ("-created_at",)


class ProgramShots(OrderedModel):
    name = models.CharField(_("Имя изображения"), null=True, max_length=50, blank=True)
    program = models.ForeignKey("guides.Program", related_name="program_shots", on_delete=models.CASCADE,
                                verbose_name=_("Программа"),
                                help_text=_("Укажите программу, к которой хотите прикрепить фото"))
    photo = ImageField(_("Изображение"),
                       upload_to=get_program_path)
    order_with_respect_to = "program"

    class Meta:
        verbose_name = _("Изображение программы")
        verbose_name_plural = _("Изображения прогамм")

    def __str__(self):
        return str(self.name) + "|" + str(self.order)

    @property
    def thumbnail_preview(self):
        if self.photo:
            _thumbnail = get_thumbnail(self.photo, '50x50', upscale=False, crop="center", quality=100)
            return format_html(
                '<img src="{}" width="{}" height="{}">'.format(_thumbnail.url, _thumbnail.width, _thumbnail.height))
        return ""


class ProgramServices(models.Model):
    title = models.CharField(_("Название услуги"), max_length=50)
    tour = models.ForeignKey("tours.Tour", verbose_name=_("Контрагент"),
                             on_delete=models.CASCADE, related_name="guide_services")

    class Meta:
        verbose_name = _("Услуги программы")
        verbose_name_plural = _("Услуги программы")

    def __str__(self):
        return self.title


class ProgramInfoSchedule(models.Model):
    program = models.ForeignKey("guides.Program", related_name="schedules", on_delete=models.CASCADE)
    title = models.CharField(_("Заголовок"), max_length=255)
    description = models.TextField(_("Описание"))
    start_time = models.TimeField(_("Время начала"))

    class Meta:
        verbose_name = _("Расписание программы")
        verbose_name_plural = _("Расписание программ")

    def __str__(self):
        return self.program.name + self.start_time.strftime("%H:%M:%") + "|" + self.title


class ProgramPlaces(models.Model):
    program = models.ForeignKey("guides.Program", related_name="places", on_delete=models.CASCADE)
    terrain = models.CharField(_("Местность"), max_length=200)
    description = models.TextField(_("Описание местности"))

    class Meta:
        verbose_name = _("Местность программы")
        verbose_name_plural = _("Местности программ")

    def __str__(self):
        return self.program.name + self.terrain
