from drf_spectacular.plumbing import build_array_type, build_basic_type
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field, OpenApiExample
from rest_framework import serializers
from sorl.thumbnail import get_thumbnail

from medtour.users.models import City


class ContentSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(default="Көктерек")
    avg_rating = serializers.SerializerMethodField(allow_null=True, default=3.5)
    slug = serializers.CharField(default="kokterek")
    obj_type = serializers.CharField(default="tour")
    shots = serializers.SerializerMethodField(allow_null=True,
                                              default=["cache/72/12/7212a7f6ff2346379687fc5a9419c039.webp"])
    city = serializers.SerializerMethodField(allow_null=True)
    price = serializers.IntegerField(read_only=True)
    category = serializers.SerializerMethodField(read_only=True)
    category_slug = serializers.SerializerMethodField(read_only=True)
    reviews_count = serializers.SerializerMethodField(read_only=True)

    @extend_schema_field(OpenApiTypes.NUMBER)
    def get_avg_rating(self, obj):
        rating_dict = {
            'service': obj.service__avg,
            'location': obj.location__avg,
            'staff': obj.staff__avg,
            'proportion': obj.proportion__avg,
        }
        if hasattr(obj, 'purity__avg'):
            rating_dict.update({'purity__avg': obj.purity__avg})
        values = [value for value in rating_dict.values() if value is not None]
        average = round(sum(values) / len(values), 2) if values else None
        return average

    @extend_schema_field(build_array_type(build_basic_type(OpenApiTypes.STR)))
    def get_shots(self, obj):
        options = {"crop": "center"}

        shots_attributes = [attr for attr in dir(obj) if attr.endswith('_shots')]
        images_attr = getattr(obj, shots_attributes[0])
        images_qs = images_attr.all()
        return [get_thumbnail(shot.photo, '570x360', **options).name for shot in images_qs]

    @extend_schema_field(OpenApiTypes.STR)
    def get_city(self, obj):
        if hasattr(obj, 'tour') and hasattr(obj.tour.city, 'name'):
            return obj.tour.city.name
        return None

    @extend_schema_field(OpenApiTypes.STR)
    def get_category(self, obj):
        return obj.tour.category.title

    @extend_schema_field(OpenApiTypes.STR)
    def get_category_slug(self, obj):
        return obj.tour.category.slug

    @extend_schema_field(OpenApiTypes.INT)
    def get_reviews_count(self, obj):
        return obj.reviews__count


class SearchCitySerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(required=True)

    class Meta:
        model = City
        fields = ('name', 'slug')


class LockedSerializer(serializers.Serializer):
    message = serializers.CharField(default='Нельзя использовать ?id__in в сущности `all`')


class CategorySerializer(serializers.Serializer):
    title = serializers.CharField()
    title_color = serializers.CharField()
    slug = serializers.CharField()
    photo = serializers.ImageField()
    icon = serializers.FileField()
    column = serializers.CharField()
    type = serializers.CharField()
    is_main = serializers.BooleanField()
