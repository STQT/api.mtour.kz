from drf_spectacular.plumbing import build_array_type, build_basic_type
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from ordered_model.serializers import OrderedModelSerializer
from rest_framework import serializers

from medtour.contrib.sorl_thumbnail_serializer.fields import HyperlinkedSorlImageField
from medtour.tournumbers.models import TourNumbers, TourNumbersServices, NumberCabinets, NumberShots, \
    NumberComfort
from medtour.tours.serializers import TourBookingExtraHolidaysSerializer
from medtour.tours.models import TourBookingExtraHolidays, TourBookingHoliday


class NumberComfortSerializer(serializers.ModelSerializer):
    # id = serializers.IntegerField()
    # name = serializers.CharField()
    # icon = serializers.FileField()

    class Meta:
        model = NumberComfort
        fields = "__all__"


class WriteTourNumbersSerializer(serializers.ModelSerializer):
    number_services = serializers.ListField(write_only=True)

    class Meta:
        model = TourNumbers
        fields = "__all__"

    def update(self, instance, validated_data):
        number_services_data = validated_data.pop("number_services", None)
        instance = super().update(instance, validated_data)
        if number_services_data:
            TourNumbersServices.objects.filter(tour_number=instance).delete()
            TourNumbersServices.objects.bulk_create(
                [
                    TourNumbersServices(tour_number=instance, title=service)
                    for service in number_services_data
                ]
            )
        if 'comforts' in validated_data:
            related_data = validated_data.pop('comforts')
            if related_data:
                instance.comforts.clear()
                instance.comforts.add(*related_data)
        return instance


class TourNumbersServicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = TourNumbersServices
        fields = ("title",)


class NumberShotsSerializer(OrderedModelSerializer):
    thumbnail = HyperlinkedSorlImageField(
        '507x203',
        options={"crop": "center"},
        source='photo',
        read_only=True
    )
    order_field_name = "order"

    class Meta:
        model = NumberShots
        fields = "__all__"


class ListNumbersSerializer(serializers.ModelSerializer):
    number_services = TourNumbersServicesSerializer(many=True, read_only=True, required=False)
    comforts = NumberComfortSerializer(many=True)
    number_shots = NumberShotsSerializer(many=True, read_only=True)

    class Meta:
        model = TourNumbers
        fields = "__all__"


class RetrieveNumbersSerializer(serializers.ModelSerializer):
    number_services = TourNumbersServicesSerializer(many=True, read_only=True, required=False)
    comforts = NumberComfortSerializer(many=True)
    numbershots_set = NumberShotsSerializer(many=True, read_only=True)
    extra_holidays = serializers.SerializerMethodField()
    holidays = serializers.SerializerMethodField()

    class Meta:
        model = TourNumbers
        fields = "__all__"

    @extend_schema_field(TourBookingExtraHolidaysSerializer(many=True))
    def get_extra_holidays(self, instance):
        extra_holidays = TourBookingExtraHolidays.objects.filter(tour=instance.tour).values("tour", "date")
        return extra_holidays

    @extend_schema_field(build_array_type(build_basic_type(OpenApiTypes.STR)))
    def get_holidays(self, instance):
        holidays = TourBookingHoliday.objects.filter(tour=instance.tour).only("days")
        if holidays.exists():
            holidays = holidays.first().days
            return holidays
        return []


class NumberCabinetsSerializer(serializers.ModelSerializer):
    class Meta:
        model = NumberCabinets
        fields = "__all__"


class NumberShotsCreateSerializer(OrderedModelSerializer):
    order_field_name = "order"

    class Meta:
        model = NumberShots
        exclude = ("order",)


class FreeNumbersSerializer(serializers.Serializer):
    title = serializers.CharField()
    count = serializers.IntegerField(default=0)
