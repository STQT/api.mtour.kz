from django.db import models
from django.db.models import Q, Min, Avg, Count
from django.http import Http404
from django.utils.translation import gettext_lazy as _, activate  # noqa F405
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import generics, mixins
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from medtour.contrib.exceptions import ImATeapot
from medtour.contrib.required_field_list_view.viewsets import TourIdRequiredFieldsModelViewSet
from medtour.contrib.serializers import ReadWriteSerializerMixin
from medtour.contrib.soft_delete_model import SoftDeleteModelViewSet
from medtour.main.serializers import ContentSerializer
from medtour.tours.serializers import (
    TourSerializer, TourPaidServicesSerializer,
    TourLocationSerializer, TourShotsSerializer,
    TourReadSerializer, CommentTourSerializer, AdditonalInfoTitleSerializer,
    AdditionalInfoServicesSerializer, TourPhonesSerializer,
    AdditionalTitlesSerializer, TourListSerializer, OrgCategorySerializer, TourPriceFileSerializer,
    CreateTourShotsSerializer, TourBookingWeekDaysSerializer, TourMedicalProfileSerializer,
    TourBookingExtraHolidaysSerializer, TourBookingHolidaySerializer,
)
from medtour.tours.models import (
    Tour, TourPaidServices, TourLocation, TourShots, CommentTour,
    TourAdditionalTitle, AdditionalInfoServices,
    TourPhones, AdditionalTitles, TourPriceFile, TourBookingWeekDays, TourMedicalProfile, Round, TourBookingExtraHolidays,
    TourBookingHoliday,
)
from medtour.tours.permissions import IsTourOwner
from medtour.users.models import OrganizationCategory


class TourViewSet(ReadWriteSerializerMixin, SoftDeleteModelViewSet):
    """
    API endpoint для туров.

    retrieve: tours/{id}/
    Возвращает конкретный тур

    list:
    Возвращает все туры которые имеют поле is_moderated=true

    me:
    Возвращает список всех туров пользователя


    CurrencyEnum:  0: "USD",
                    1: "KZT",
                    2: "UZS",
                    3: "KGS",
                    4: "EUR",
    """
    queryset = Tour.objects.all()
    write_serializer_class = TourSerializer
    read_serializer_class = TourReadSerializer
    list_serializer_class = TourListSerializer
    filterset_fields = ['region_id', "category_id", "country_id",
                        "org_id", "org__user_id", "category__slug"]
    parser_classes = (MultiPartParser, JSONParser)
    # pagination_class = TourStandardResultsSetPagination
    detail_pr_related_tuple = ("tour_shots", "additional_titles__title",
                               "additional_titles__additional_services", "comments__user",
                               "medical_profiles"
                               )
    detail_sl_related_tuple = ("region", "country", "category", "org__user")
    list_pr_related_tuple = (
        "tour_shots",
    )
    list_sl_related_tuple = ("org__user", "category", "region")
    permission_classes = [IsTourOwner]

    @extend_schema(summary="Туры", description="Для подробного просмотра своих туров. "
                                               "Если тур не прошёл модерацию, "
                                               "то только будет видно только самому пользователю",
                   )
    @action(detail=False)
    def me(self, request):
        if isinstance(self.request.user.id, int) is False:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data={"message": "Unauthorized"})
        queryset = self.get_queryset().filter(org__user=request.user)

        serializer = self.read_serializer_class(queryset, many=True)
        return Response(serializer.data)

    # TODO: needs to uncommitted if data is biggest
    # def list(self, request, *args, **kwargs):
    #     result_id = request.query_params.get('result_id')
    #     if result_id:
    #         result = cache.get(result_id)
    #         if result:
    #             page = self.paginate_queryset(result)
    #             serializer = self.get_serializer(page, many=True)
    #             resp = self.get_paginated_response(serializer.data)
    #             resp.data['result_id'] = result_id
    #             return resp
    #     queryset = self.filter_queryset(self.get_queryset())
    #     # Only works for paginated results
    #     page = self.paginate_queryset(queryset)
    #     serializer = self.get_serializer(page, many=True)
    #     result_id = generate_unique_identifier()
    #     cache.set(result_id, queryset)
    #     resp = self.get_paginated_response(serializer.data)
    #     resp.data['result_id'] = result_id
    #     return resp

    @action(detail=False)
    def medicalProfiles(self, request, *args, **kwargs):  # noqa
        obj = TourMedicalProfile.objects.all()
        serializer = TourMedicalProfileSerializer(obj, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == "list":
            return qs.filter(
                is_deleted=False, is_moderated=True
            ).annotate(
                minimum_price=Min("numbers__price", filter=Q(numbers__is_deleted=False)),
                service__avg=Round(Avg('comments__service'), 2, output_field=models.FloatField()),
                location__avg=Round(Avg('comments__location'), 2, output_field=models.FloatField()),
                purity__avg=Round(Avg('comments__purity'), 2, output_field=models.FloatField()),
                staff__avg=Round(Avg('comments__staff'), 2, output_field=models.FloatField()),
                proportion__avg=Round(Avg('comments__proportion'), 2, output_field=models.FloatField()),
                comments__count=Count('comments__purity', output_field=models.FloatField())
            ).prefetch_related(
                *self.list_pr_related_tuple
            ).select_related(
                *self.list_sl_related_tuple
            ).order_by("?")
        elif self.action == "retrieve":
            return qs.select_related(*self.detail_sl_related_tuple).prefetch_related(*self.detail_pr_related_tuple)
        return qs

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return self.get_write_serializer_class()
        elif self.action == "list":
            return self.list_serializer_class
        return self.get_read_serializer_class()


class OrgCategoryView(viewsets.ModelViewSet):
    queryset = OrganizationCategory.objects.all()
    serializer_class = OrgCategorySerializer
    http_method_names = ["get"]
    lookup_field = "slug"


class TourShotsView(TourIdRequiredFieldsModelViewSet):  # noqa F405
    """Эндпоинт для изображения туров"""
    serializer_class = TourShotsSerializer
    create_serializer_class = CreateTourShotsSerializer
    queryset = TourShots.objects.all()  # prefetch_related("tour")
    parser_classes = (MultiPartParser, JSONParser)
    filterset_fields = ["tour_id"]

    def get_serializer_class(self):
        if self.action in ["create"]:
            return self.create_serializer_class
        return self.serializer_class

    @extend_schema(parameters=[OpenApiParameter(
        name="ids",
        description="Чтобы удалять фотки укажите в виде ?ids=1,2,3,4...")
    ],
        summary="Удаление нескольких фоток за раз")
    @action(methods=["DELETE"], detail=False)
    def delete(self, request):
        delete_id = request.query_params.get('ids')
        id_list: list = delete_id.split(",")
        delete_albums = self.queryset.filter(id__in=id_list)

        delete_albums.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TourPhonesView(TourIdRequiredFieldsModelViewSet):
    queryset = TourPhones.objects.all()
    serializer_class = TourPhonesSerializer
    filterset_fields = ["tour_id"]


class TourPaidServicesView(TourIdRequiredFieldsModelViewSet):  # noqa F405
    """Дополнительные платные услуги"""
    queryset = TourPaidServices.objects.all()  # .prefetch_related("tour")
    serializer_class = TourPaidServicesSerializer
    serializer_classes = {
        "create"
    }
    # filterset_fields = ["tour_id", "ids"]
    filterset_fields = {
        "id": ["exact", "in"],
        "tour_id": ["exact"],
    }

    def get_queryset(self):
        if self.request.query_params.get("id__in") == "":
            raise ImATeapot
        qs = super().get_queryset()
        return qs


class TourLocationView(TourIdRequiredFieldsModelViewSet):
    """Локации тура"""
    queryset = TourLocation.objects.all()
    serializer_class = TourLocationSerializer
    filterset_fields = ["tour_id"]

    @extend_schema(summary="Локация конкретного тура",
                   parameters=[
                       OpenApiParameter(name="id",
                                        description="Введите id тура",
                                        required=True), ]
                   )
    @action(detail=False)
    def tour(self, request, *args, **kwargs):
        obj = self.get_queryset().filter(tour_id=request.query_params.get('id')).first()
        serializer = self.get_serializer(obj, many=False)
        return Response(serializer.data)


class TourCommentView(TourIdRequiredFieldsModelViewSet):
    serializer_class = CommentTourSerializer
    queryset = CommentTour.objects.all()
    http_method_names = ["get", "post"]
    filterset_fields = ["tour_id"]


class AdditionalTitleViewset(TourIdRequiredFieldsModelViewSet):
    """Здесь есть возможность создания своих названий туров и
    возвращаются те которые не прикреплены к конкретному турID
    """
    queryset = AdditionalTitles.objects.all()
    serializer_class = AdditionalTitlesSerializer
    filterset_fields = ["tour_id"]

    def filter_queryset(self, queryset):
        if self.request.query_params.get('tour_id'):
            return queryset.filter(Q(tour_id=self.request.query_params.get('tour_id')) | Q(tour__isnull=True))
        return queryset


class AdditionalInfoTitleViewSet(TourIdRequiredFieldsModelViewSet):
    """Здесь создаётся заголовки к турам
    GET additionalInfo/ для получения всех Заголовках во всех турах,
    чтобы получить заголовки конкретного тура добавьте к параметрам
    ?tour_id={id}
    POST additionalInfo/
    для добавления к конкретному туру заголовок внутри даты добавьте
    запись tour: {id}
    """
    queryset = TourAdditionalTitle.objects.all()
    serializer_class = AdditonalInfoTitleSerializer
    filterset_fields = ["tour_id"]


class AdditionalInfoServicesViewSet(viewsets.ModelViewSet):
    """Здесь создаётся услуга к заголовкам
        GET additionalInfoServices/ для получения всех Услуг во всех Заголовках,
        чтобы получить заголовки конкретного тура добавьте к параметрам
        ?title_id={id}
        POST additionalInfo/
        для добавления к конкретному туру заголовок внутри даты добавьте
        запись title: {id}
        service: {string}
        """
    queryset = AdditionalInfoServices.objects.all()  # .prefetch_related("title", "tour")
    serializer_class = AdditionalInfoServicesSerializer
    filterset_fields = ["title_id"]

    @extend_schema(
        parameters=[OpenApiParameter(name="title_id", required=True, type=int, location=OpenApiParameter.PATH)])
    def list(self, request, *args, **kwargs):
        super(self).list(request, *args, **kwargs)


class TourPriceFileView(TourIdRequiredFieldsModelViewSet):
    queryset = TourPriceFile.objects.all()
    serializer_class = TourPriceFileSerializer
    filterset_fields = "tour_id",
    required_fields = ["tour_id"]


class TourBookingWeekDaysViewSet(mixins.RetrieveModelMixin,
                                 mixins.UpdateModelMixin,
                                 GenericViewSet):
    """<b>Дни недели для указания заезда в заведение</b>"""
    queryset = TourBookingWeekDays.objects.all()
    serializer_class = TourBookingWeekDaysSerializer
    lookup_field = "tour_id"


class TourSlugView(generics.RetrieveAPIView):
    queryset = Tour.objects.select_related(
        "region", "country", "category", "org__user"
    ).prefetch_related(
        "services", "tour_shots", "additional_titles__title",
        "additional_titles__additional_services", "comments__user"
    )
    serializer_class = TourReadSerializer
    lookup_field = 'slug'
    lookup_url_kwarg = 'slug'

    def get_object(self):
        try:
            obj = self.queryset.get(slug=self.kwargs.get(self.lookup_url_kwarg))
        except Tour.DoesNotExist:
            raise Http404
        return obj


class TourManyViewWithoutPagination(generics.ListAPIView):
    queryset = Tour.objects.annotate(
        minimum_price=Min("numbers__price", filter=Q(numbers__is_deleted=False)),
        service__avg=Round(Avg('comments__service'), 2, output_field=models.FloatField()),
        location__avg=Round(Avg('comments__location'), 2, output_field=models.FloatField()),
        purity__avg=Round(Avg('comments__purity'), 2, output_field=models.FloatField()),
        staff__avg=Round(Avg('comments__staff'), 2, output_field=models.FloatField()),
        proportion__avg=Round(Avg('comments__proportion'), 2, output_field=models.FloatField()),
        comments__count=Count('comments__purity', output_field=models.FloatField())
    ).prefetch_related('tour_shots').select_related("org__user", "category", "region")
    serializer_class = ContentSerializer

    @extend_schema(summary="Получение много туров по конкретным id",
                   parameters=[OpenApiParameter(name="id__in", description="Введите id__in туров", required=True)],
                   responses={'200': TourListSerializer(many=True)},
                   )
    @action(detail=False)
    def get(self, request, *args, **kwargs):  # noqa
        ids = request.query_params.get('id__in')  # noqa
        if not ids:
            return Response({"message": _("Обязательный параметр id__in не указан.")},
                            status=status.HTTP_400_BAD_REQUEST)
        qs = self.get_queryset().filter(id__in=ids.split(','))
        serializer = self.serializer_class(qs, many=True)
        return Response(serializer.data)


class TourBookingHolidayViewSet(mixins.RetrieveModelMixin,
                                mixins.UpdateModelMixin,
                                GenericViewSet):
    """<b>Ценообразование по дню недели.
    Там, где указан день, цена будет выше</b>"""
    queryset = TourBookingHoliday.objects.all()
    serializer_class = TourBookingHolidaySerializer
    lookup_field = "tour_id"


class TourBookingExtraHolidaysViewSet(mixins.CreateModelMixin,
                                      mixins.UpdateModelMixin,
                                      mixins.DestroyModelMixin,
                                      GenericViewSet):
    queryset = TourBookingExtraHolidays.objects.all()
    serializer_class = TourBookingExtraHolidaysSerializer

#
# class MyView(APIView):
#     def get(self, request):
#         language = request.META.get('HTTP_ACCEPT_LANGUAGE', 'en')
#         print(language)
#         activate(language)
#         queryset = BlaBlaCar.objects.all()
#         serializer = MySerializer(queryset, many=True, context={'language': language})
#
#         return Response(serializer.data)
