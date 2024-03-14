from datetime import date

from django.utils.translation import gettext_lazy as _  # noqa F405
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status, generics, permissions
from rest_framework.decorators import action
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.response import Response

from medtour.contrib.exceptions import ImATeapot
from medtour.contrib.required_field_list_view.viewsets import (TourIdRequiredSoftDeleteModelViewSet,
                                                               TourNumberRequiredFieldsModelViewSet,
                                                               TourNumberRequiredSoftDeleteModelViewSet)
from medtour.contrib.serializers import ReadWriteSerializerMixin
from medtour.tournumbers.permissions import IsTourNumberOwner
from medtour.tournumbers.serializers import (
    ListNumbersSerializer, WriteTourNumbersSerializer, NumberCabinetsSerializer,
    NumberComfortSerializer, NumberShotsSerializer, NumberShotsCreateSerializer, FreeNumbersSerializer,
    RetrieveNumbersSerializer
)
from medtour.tournumbers.models import (
    TourNumbers, TourNumbersServices, NumberCabinets, NumberComfort,
    NumberShots)


class TourNumbersView(ReadWriteSerializerMixin, TourIdRequiredSoftDeleteModelViewSet):
    queryset = TourNumbers.objects.prefetch_related("comforts")
    # TODO splitting for weekdays and holidays aggregating get_object method
    read_serializer_class = ListNumbersSerializer
    retrieve_serializer_class = RetrieveNumbersSerializer
    write_serializer_class = WriteTourNumbersSerializer
    filterset_fields = {
        "id": ["exact", "in"],
        "tour_id": ["exact"],
        "tour__slug": ["exact"],
    }

    def get_permissions(self):
        if self.action == "free_numbers":
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [IsTourNumberOwner]
        return [permission() for permission in permission_classes]

    @action(detail=False)
    def comforts(self, request, *args, **kwargs):
        queryset = NumberComfort.objects.all()
        serializer = NumberComfortSerializer(queryset, many=True)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)

    def get_queryset(self):
        if self.request.query_params.get("id__in") == "":
            raise ImATeapot
        queryset = super().get_queryset()
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            """ Валидация ПОСТ запроса"""
            validated_data = serializer.validated_data
            number_services = validated_data.pop('number_services', "")
            if type(number_services) is str:
                number_services = number_services.split(",")
            instance = serializer.save()
            TourNumbersServices.objects.bulk_create(
                [
                    TourNumbersServices(tour_number=instance, title=service)
                    for service in number_services
                ]
            )
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        parameters=[
            OpenApiParameter(name="tour_id", required=True, type=int),
            OpenApiParameter(name="today", required=True, type=date)
        ])
    @action(detail=False)
    def free_numbers(self, request, *args, **kwargs):
        tour_id = self.request.query_params.get('tour_id')
        today = self.request.query_params.get('today')
        if not tour_id and not today:
            return Response(
                {
                    "message": _("Обязательный параметр tour_id и today не указан.")},
                status=status.HTTP_400_BAD_REQUEST)

        queryset = TourNumbers.objects.values("title")
        serializer = FreeNumbersSerializer(queryset, many=True)
        return Response(serializer.data)


class NumberCabinetsView(TourNumberRequiredSoftDeleteModelViewSet):
    queryset = NumberCabinets.objects.all()
    serializer_class = NumberCabinetsSerializer
    filterset_fields = {
        "tour_number_id": ["exact"],
        "tour_number__tour_id": ["exact"],
    }


class NumberShotsViewSet(TourNumberRequiredFieldsModelViewSet):
    queryset = NumberShots.objects.all()
    serializer_class = NumberShotsSerializer
    create_serializer_class = NumberShotsCreateSerializer
    parser_classes = (MultiPartParser, JSONParser)
    filterset_fields = {
        "tour_number_id": ["exact"]
    }

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


class NumberComfortView(generics.ListAPIView):
    queryset = NumberComfort.objects.all()
    serializer_class = NumberComfortSerializer
