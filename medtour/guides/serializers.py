from django.utils.translation import gettext_lazy as _
from drf_spectacular import types
from drf_spectacular.utils import extend_schema_field
from ordered_model.serializers import OrderedModelSerializer
from rest_framework import serializers
from rest_framework.filters import OrderingFilter

from medtour.contrib.sorl_thumbnail_serializer.fields import HyperlinkedSorlImageField
from medtour.guides.models import (
    Program, ProgramServices, ProgramInfoSchedule,
    ProgramPlaces, ProgramShots, ProgramReview, ProgramServices, ProgramPrice)
from medtour.tours.models import TourShots
from medtour.users.serializers import CountrySerializer, RegionSerializer
from medtour.utils.constants import LanguagesChoice


class GuideServicesSmallSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()


class ProgramReviewSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(source="user.avatar", read_only=True, allow_null=True, required=False)  # noqa
    userData = serializers.SerializerMethodField(read_only=True, allow_null=True)

    class Meta:
        model = ProgramReview
        fields = "__all__"

    @extend_schema_field(types.OpenApiTypes.STR)
    def get_userData(self, instance):
        if hasattr(instance.user, "people"):
            return instance.user.people.first_name + " " + instance.user.people.last_name
        elif hasattr(instance.user, "organization"):
            return instance.user.organization.org_name
        return _("Удалённый аккаунт")


class AverageGuideRatingSerializer(serializers.Serializer):
    service__avg = serializers.FloatField(allow_null=True)
    location__avg = serializers.FloatField(allow_null=True)
    staff__avg = serializers.FloatField(allow_null=True)
    proportion__avg = serializers.FloatField(allow_null=True)
    reviews__count = serializers.IntegerField(allow_null=True)


class ProgramInfoScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramInfoSchedule
        fields = "__all__"


class ProgramPlacesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramPlaces
        fields = "__all__"


class ProgramSerializer(serializers.ModelSerializer):
    languages = serializers.MultipleChoiceField(choices=LanguagesChoice.choices)

    class Meta:
        model = Program
        fields = "__all__"


class ProgramShotsSerializer(serializers.ModelSerializer):
    thumbnail = HyperlinkedSorlImageField(
        '570x360',
        options={"crop": "center"},
        source='photo',
        read_only=True
    )

    class Meta:
        model = ProgramShots
        fields = ("thumbnail",)


class ProgramListSerializer(serializers.ModelSerializer):
    program_shots = ProgramShotsSerializer(many=True, read_only=True)

    class Meta:
        model = Program
        fields = ["id", "name", "program_shots", "seats_count"]


class ProgramPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramPrice
        fields = "__all__"


class ProgramDetailSerializer(serializers.ModelSerializer):
    languages = serializers.MultipleChoiceField(choices=LanguagesChoice.choices)
    program_shots = ProgramShotsSerializer(many=True)
    services = GuideServicesSmallSerializer(read_only=True, many=True)
    excluded_services = GuideServicesSmallSerializer(read_only=True, many=True)
    guide_name = serializers.StringRelatedField(source='guide.title')
    average_rating = serializers.SerializerMethodField()
    schedules = serializers.SerializerMethodField()
    places = ProgramPlacesSerializer(many=True, label="Местности программы")
    program_prices = ProgramPriceSerializer(many=True)

    class Meta:
        model = Program
        fields = "__all__"

    @extend_schema_field(ProgramInfoScheduleSerializer(many=True, label="Расписание программы гида"))
    def get_schedules(self, obj):
        schedules = obj.schedules.all().order_by('start_time')
        serializer = ProgramInfoScheduleSerializer(schedules, many=True)
        return serializer.data

    @extend_schema_field(AverageGuideRatingSerializer)
    def get_average_rating(self, instance):
        return instance.guide.average_rating


class ProgramServicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramServices
        fields = "__all__"
