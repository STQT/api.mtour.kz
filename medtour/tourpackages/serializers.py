from drf_spectacular.plumbing import build_array_type, build_basic_type
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from medtour.contrib.serializers import StringArrayField
from medtour.tournumbers.serializers import ListNumbersSerializer
from medtour.tourpackages.models import TourPackages, TourPackagesServices
from medtour.tours.serializers import TourBookingExtraHolidaysSerializer
from medtour.tours.models import TourBookingExtraHolidays, TourBookingHoliday


class WriteTourPackageSerializer(serializers.ModelSerializer):
    package_services = StringArrayField(write_only=True)

    class Meta:
        model = TourPackages
        fields = "__all__"

    def update(self, instance, validated_data):
        package_services = validated_data.pop('package_services')
        if package_services:
            TourPackagesServices.objects.filter(package_id=instance.id).delete()
            TourPackagesServices.objects.bulk_create(
                [
                    TourPackagesServices(package=instance, title=service)
                    for service in package_services
                ]
            )
        return super().update(instance, validated_data)


class TourPackageServicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = TourPackagesServices
        fields = "__all__"


class ListPackageSerializer(serializers.ModelSerializer):
    package_services = TourPackageServicesSerializer(many=True, read_only=True, required=False)
    number = ListNumbersSerializer(many=False, read_only=True)

    class Meta:
        model = TourPackages
        fields = "__all__"


class RetrievePackageSerializer(serializers.ModelSerializer):
    package_services = TourPackageServicesSerializer(many=True, read_only=True, required=False)
    number = ListNumbersSerializer(many=False, read_only=True)
    extra_holidays = serializers.SerializerMethodField()
    holidays = serializers.SerializerMethodField()

    class Meta:
        model = TourPackages
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
