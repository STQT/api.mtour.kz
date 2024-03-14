import uuid
from datetime import datetime

from django.utils.translation import gettext_lazy as _
from drf_spectacular import types
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from ordered_model.serializers import OrderedModelSerializer
from rest_framework import serializers

from medtour.contrib.sorl_thumbnail_serializer.fields import HyperlinkedSorlImageField
from medtour.guides.models import Guide
from medtour.orders.models import Payment
from medtour.tours.models import (
    Tour, TourLocation, TourPaidServices, TourAdditionalTitle,
    TourShots, CommentTour, AdditionalInfoServices,
    TourPhones, AdditionalTitles, TourPriceFile, TourBookingWeekDays,
    TourBookingExtraHolidays, TourBookingHoliday)
from medtour.users.serializers import RegionSerializer, CountrySerializer
from medtour.users.models import OrganizationCategory, Organization
from medtour.utils.constants import WeekDayChoice


class TourShotsSerializer(OrderedModelSerializer):
    order_field_name = "order"

    class Meta:
        model = TourShots
        fields = "__all__"


class CreateTourShotsSerializer(OrderedModelSerializer):
    order_field_name = "order"

    class Meta:
        model = TourShots
        exclude = ("order",)


class DetailViewTourShotsSerializer(serializers.ModelSerializer):
    thumbnail = HyperlinkedSorlImageField(
        '752x350',
        options={"crop": "center"},
        source='photo',
        read_only=True
    )

    class Meta:
        model = TourShots
        fields = "__all__"


class MainPageTourShotsSerializer(serializers.ModelSerializer):
    thumbnail = HyperlinkedSorlImageField(
        '570x360',
        options={"crop": "center"},
        source='photo',
        read_only=True
    )

    class Meta:
        model = TourShots
        fields = "__all__"


class TourMedicalProfileSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class TourPriceFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TourPriceFile
        fields = "__all__"


class TourPhonesSerializer(serializers.ModelSerializer):
    phone = serializers.SerializerMethodField()

    class Meta:
        model = TourPhones
        fields = "__all__"

    @extend_schema_field(OpenApiTypes.STR)
    def get_phone(self, obj):
        return "+7 (700) 110 81-30"


class TourLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TourLocation
        fields = "__all__"


class TourPaidServicesSerializer(serializers.ModelSerializer):
    """Сериалайзер для платных услуг тура"""

    class Meta:
        model = TourPaidServices
        fields = "__all__"


class OrgCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationCategory
        fields = "__all__"


class TourSerializer(serializers.ModelSerializer):
    org = serializers.PrimaryKeyRelatedField(queryset=Organization.objects.all())
    is_moderated = serializers.BooleanField(default=True, read_only=True)

    class Meta:
        model = Tour
        exclude = ("created_at", "is_deleted", "is_subscribed", "is_top")


class CommentTourSerializer(serializers.ModelSerializer):
    userData = serializers.SerializerMethodField(read_only=True, allow_null=True)

    # user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = CommentTour
        fields = "__all__"

    @extend_schema_field(types.OpenApiTypes.STR)
    def get_userData(self, instance):
        if hasattr(instance.user, "people"):
            return instance.user.people.first_name + " " + instance.user.people.last_name
        elif hasattr(instance.user, "organization"):
            return instance.user.organization.org_name
        return _("Удалённый аккаунт")

    def validate(self, attrs):
        # check if user has already commented this tour
        comment = CommentTour.objects.filter(user=attrs['user'], tour=attrs['tour']).first()
        if comment:
            raise serializers.ValidationError("Вы уже оставили отзыв")
        payments = Payment.objects.filter(user=attrs['user'], tour=attrs['tour']).first()
        if payments and payments.cart.date_end < datetime.now():
            raise serializers.ValidationError("Вы не можете оставить отзыв так как не прошел срок вашего прибывания")

        return attrs


class AdditionalTitlesSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = AdditionalTitles


class AdditionalInfoServicesReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdditionalInfoServices
        fields = ("service", "id")


class AdditionalInfoServicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdditionalInfoServices
        fields = "__all__"


class AdditonalInfoTitleSerializer(serializers.ModelSerializer):
    additional_services = AdditionalInfoServicesReadSerializer(many=True, read_only=True)
    title_name = serializers.StringRelatedField(source="title.name")

    class Meta:
        model = TourAdditionalTitle
        fields = "__all__"


class AverageRating(serializers.Serializer):
    service__avg = serializers.FloatField(allow_null=True)
    purity__avg = serializers.FloatField(allow_null=True)
    location__avg = serializers.FloatField(allow_null=True)
    staff__avg = serializers.FloatField(allow_null=True)
    proportion__avg = serializers.FloatField(allow_null=True)
    comments__count = serializers.IntegerField(allow_null=True)


def generate_unique_identifier():
    # Generate a UUID (Universally Unique Identifier) as the unique identifier
    return str(uuid.uuid4())


def perform_expensive_operation():
    # Simulate an expensive operation that takes some time to complete
    result = []
    for i in range(1000000):
        result.append(i)
    return result


class TourListSerializer(serializers.ModelSerializer):
    region_name = serializers.StringRelatedField(source="region.name", allow_null=True, required=False)
    category_name = serializers.StringRelatedField(source="category.title", allow_null=True)
    minimum_price = serializers.IntegerField()
    tour_shots = MainPageTourShotsSerializer(read_only=True, many=True, required=False, allow_null=True)
    category_slug = serializers.StringRelatedField(source="category.slug")
    averageRating = serializers.SerializerMethodField()

    class Meta:
        model = Tour
        fields = ("id", "title", "description", "region_name",
                  "category_name", "category", "minimum_price", "tour_shots",
                  "category_slug", "slug", "averageRating")

    @extend_schema_field(AverageRating)
    def get_averageRating(self, instance):
        return {
            "minimum_price": instance.minimum_price,
            "service__avg": instance.service__avg,
            "location__avg": instance.location__avg,
            "purity__avg": instance.purity__avg,
            "staff__avg": instance.staff__avg,
            "proportion__avg": instance.proportion__avg,
            "comments__count": instance.comments__count,
        }


class TourReadSerializer(serializers.ModelSerializer):
    category_slug = serializers.StringRelatedField(source="category.slug")
    tour_shots = DetailViewTourShotsSerializer(read_only=True, many=True, required=False, allow_null=True)
    comments = CommentTourSerializer(read_only=True, many=True, required=False, allow_null=True)
    region = RegionSerializer(many=False, read_only=True)
    country = CountrySerializer(many=False, read_only=True)
    averageRating = serializers.SerializerMethodField()
    additional_titles = AdditonalInfoTitleSerializer(many=True, read_only=True)
    medical_profiles = TourMedicalProfileSerializer(many=True)
    numbers_exists = serializers.SerializerMethodField()
    guides_exists = serializers.SerializerMethodField()
    paid_services_exists = serializers.SerializerMethodField()
    packages_exists = serializers.SerializerMethodField()

    class Meta:
        model = Tour
        exclude = ('created_at', "is_subscribed")

    @extend_schema_field(AverageRating)
    def get_averageRating(self, instance):
        return instance.average_rating

    @extend_schema_field(serializers.BooleanField)
    def get_numbers_exists(self, instance):
        return instance.numbers.exists()

    @extend_schema_field(serializers.BooleanField)
    def get_guides_exists(self, instance):
        return Guide.objects.filter(region_id=instance.region_id).exists()

    @extend_schema_field(serializers.BooleanField)
    def get_packages_exists(self, instance):
        return instance.packages.exists()

    @extend_schema_field(serializers.BooleanField)
    def get_paid_services_exists(self, instance):
        return instance.services.exists()


class TourBookingWeekDaysSerializer(serializers.ModelSerializer):
    days = serializers.MultipleChoiceField(choices=WeekDayChoice.choices)

    class Meta:
        model = TourBookingWeekDays
        exclude = ("id",)


#
# class MySerializer(serializers.ModelSerializer):
#     name = serializers.SerializerMethodField()
#
#     def get_name(self, obj):
#         language = self.context.get('language', 'en')
#         if language == 'en':
#             return _(obj.name)
#         elif language == 'fr' and obj.name_fr:
#             return _(obj.name_fr)
#         elif language == 'es' and obj.name_es:
#             return _(obj.name_es)
#         else:
#             # If language is not translatable, use Google Translate API
#             url = 'https://translation.googleapis.com/language/translate/v2'
#             params = {
#                 'key': settings.GOOGLE_API,
#                 'q': obj.name,
#                 'source': settings.LANGUAGE_CODE,
#                 'target': language,
#             }
#             response = requests.post(url, params=params).json()
#             translated_text = response['data']['translations'][0]['translatedText']
#             return _(translated_text)
#     class Meta:
#         model = BlaBlaCar
#         fields = ['name']


class TourBookingExtraHolidaysSerializer(serializers.ModelSerializer):
    class Meta:
        model = TourBookingExtraHolidays
        fields = "__all__"


class TourBookingHolidaySerializer(serializers.ModelSerializer):
    days = serializers.MultipleChoiceField(choices=WeekDayChoice.choices)
    extra_holidays = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = TourBookingHoliday
        fields = "__all__"

    @extend_schema_field(TourBookingExtraHolidaysSerializer(many=True))
    def get_extra_holidays(self, instance):
        extra_holidays = TourBookingExtraHolidays.objects.filter(tour=instance.tour).values("tour", "date", "id")
        return extra_holidays
