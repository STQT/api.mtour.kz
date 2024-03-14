from django.db import models
from django.db.models import Min, Avg, Count, Q, Value
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import generics, status
from rest_framework.response import Response

from itertools import chain

from rest_framework.views import APIView

from medtour.guides.models import Guide, Round, GuideCategory
from medtour.main.filters import CityFilter
from medtour.main.serializers import ContentSerializer, SearchCitySerializer, LockedSerializer, CategorySerializer
from medtour.tours.models import Tour
from medtour.users.models import City, OrganizationCategory


def get_tours(filters):
    tour_qs = Tour.objects.filter(**filters).annotate(
        minimum_price=Min("numbers__price", filter=Q(numbers__is_deleted=False)),
        service__avg=Round(Avg('comments__service'), 2, output_field=models.FloatField()),
        location__avg=Round(Avg('comments__location'), 2, output_field=models.FloatField()),
        purity__avg=Round(Avg('comments__purity'), 2, output_field=models.FloatField()),
        staff__avg=Round(Avg('comments__staff'), 2, output_field=models.FloatField()),
        proportion__avg=Round(Avg('comments__proportion'), 2, output_field=models.FloatField()),
        comments__count=Count('comments__purity', output_field=models.FloatField()),
        type=Value('tours', output_field=models.CharField()),
    ).prefetch_related("tour_shots").select_related('city').order_by('is_top')
    return tour_qs


def get_guides(filters):
    guides_queryset = Guide.objects.filter(**filters).annotate(
        minimum_price=Min("programs__price", filter=Q(programs__is_deleted=False)),
        service__avg=Round(Avg('guide_reviews__service'), 2, output_field=models.FloatField()),
        location__avg=Round(Avg('guide_reviews__location'), 2, output_field=models.FloatField()),
        staff__avg=Round(Avg('guide_reviews__staff'), 2, output_field=models.FloatField()),
        proportion__avg=Round(Avg('guide_reviews__proportion'), 2, output_field=models.FloatField()),
        comments__count=Count('guide_reviews__service', output_field=models.FloatField()),
        type=Value('guides', output_field=models.CharField()),
    ).prefetch_related('guide_shots').select_related('city')
    return guides_queryset


class ToursGuidesView(APIView):
    serializer_class = ContentSerializer
    queryset = Tour.objects.all()  # F405

    @extend_schema(
        parameters=[
            OpenApiParameter("category__slug", type=OpenApiTypes.STR, many=False),
            OpenApiParameter("id__in", type=OpenApiTypes.INT, many=True),
            OpenApiParameter("is_top", type=OpenApiTypes.BOOL, many=False),
        ],
        responses={"200": ContentSerializer,
                   "423": LockedSerializer}
    )
    def get(self, request, city, entity, *args, **kwargs):
        filters = {
            'is_moderated': True,
            'is_deleted': False,
        }

        if city != "all":
            filters['city__slug'] = city

        id__in = request.query_params.getlist('id__in')
        if id__in and entity != "all":
            filters['id__in'] = [int(pk) for pk in id__in]

        category__slug = request.query_params.get('category__slug')
        if category__slug:
            filters['category__slug'] = category__slug  # noqa

        is_top = request.query_params.get("is_top")
        if is_top:
            filters["is_top"] = True if is_top == "true" else False
        if entity == "all":
            if id__in:
                return Response(
                    {
                        "message": _(f"В сущности `all` не работает параметр ?id__in")},
                    status=status.HTTP_423_LOCKED)
            combined_queryset = chain(get_tours(filters),
                                      get_guides(filters))
            serializer = ContentSerializer(combined_queryset, many=True)
        elif entity == "tours":
            serializer = ContentSerializer(get_tours(filters), many=True)
        elif entity == "guides":
            serializer = ContentSerializer(get_guides(filters), many=True)
        else:
            return Response(
                {
                    "message": _(f"Вы неверно указали сущность: {entity}").format(entity=entity)
                },
                status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data)


class CitySearchAPIView(generics.ListAPIView):
    """
    Поиск городов по значениям.
    TODO: в дальнейшем будет по регионам и по странам.
    """
    queryset = City.objects.filter(is_first_page=True)
    serializer_class = SearchCitySerializer
    filterset_class = CityFilter

    @method_decorator(cache_page(60 * 15))  # Cache for 15 minutes
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class CategoriesListAPIView(APIView):
    serializer_class = CategorySerializer

    def get(self, request):
        combined_queryset = chain(
            OrganizationCategory.objects.annotate(
                type=Value('tours', output_field=models.CharField())
            ),
            GuideCategory.objects.annotate(
                type=Value('guides', output_field=models.CharField()),
            )
        )
        serializer = self.serializer_class(combined_queryset, many=True)
        return Response(serializer.data)
