from django.utils.translation import gettext_lazy as _
from drf_spectacular import types
from drf_spectacular.utils import extend_schema_field
from ordered_model.serializers import OrderedModelSerializer
from rest_framework import serializers

from medtour.contrib.sorl_thumbnail_serializer.fields import HyperlinkedSorlImageField
from medtour.guides.models import Guide, GuideProgram, GuideReview, GuideServices, GuideShots
from medtour.users.serializers import CountrySerializer, RegionSerializer


class GuideServicesSmallSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()


class GuideReviewSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(source="user.avatar", read_only=True, allow_null=True, required=False)
    userData = serializers.SerializerMethodField(read_only=True, allow_null=True)

    class Meta:
        model = GuideReview
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


class GuidePOSTShotsSerializer(OrderedModelSerializer):
    thumbnail = HyperlinkedSorlImageField(
        '752x350',
        options={"crop": "center"},
        source='photo',
        read_only=True
    )

    class Meta:
        model = GuideShots
        exclude = ("order", )


class GuideShotsSerializer(OrderedModelSerializer):
    thumbnail = HyperlinkedSorlImageField(
        '752x350',
        options={"crop": "center"},
        source='photo',
        read_only=True
    )

    class Meta:
        model = GuideShots
        fields = "__all__"


class GuideSerializer(serializers.ModelSerializer):
    guide_shots = GuideShotsSerializer(read_only=True, many=True, required=False, allow_null=True)
    minimum_price = serializers.IntegerField(read_only=True, default=0)
    is_moderated = serializers.BooleanField(default=True, read_only=True)

    class Meta:
        model = Guide
        exclude = ("created_at", "is_deleted", "is_subscribed", "is_top")


class GuideReadSerializer(serializers.ModelSerializer):
    region = RegionSerializer(many=False, read_only=True)
    country = CountrySerializer(many=False, read_only=True)
    average_rating = serializers.SerializerMethodField()
    guide_shots = GuideShotsSerializer(read_only=True, many=True, required=False, allow_null=True)

    class Meta:
        model = Guide
        fields = "__all__"

    @extend_schema_field(AverageGuideRatingSerializer)
    def get_average_rating(self, instance):
        return instance.average_rating


class GuideListSerializer(serializers.ModelSerializer):
    guide_shots = GuideShotsSerializer(read_only=True, many=True, required=False, allow_null=True)
    minimum_price = serializers.IntegerField(read_only=True, default=0)
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Guide
        fields = ("id", "title", "guide_shots", "minimum_price", "average_rating")

    @extend_schema_field(AverageGuideRatingSerializer)
    def get_average_rating(self, instance):
        return instance.average_rating


class GuideProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuideProgram
        fields = "__all__"


class GuideProgramListSerializer(serializers.ModelSerializer):
    thumbnail = HyperlinkedSorlImageField(
        '752x350',
        options={"crop": "center"},
        source='photo',
        read_only=True
    )

    class Meta:
        model = GuideProgram
        exclude = ["services", "venue_lon", "venue_lat", "venue_address", "description"]


class GuideProgramDetailSerializer(serializers.ModelSerializer):
    thumbnail = HyperlinkedSorlImageField(
        '752x350',
        options={"crop": "center"},
        source='photo',
        read_only=True
    )
    services = GuideServicesSmallSerializer(read_only=True, many=True)

    class Meta:
        model = GuideProgram
        fields = "__all__"


class GuideServicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuideServices
        fields = "__all__"
