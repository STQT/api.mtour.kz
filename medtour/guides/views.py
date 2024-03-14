from django.db.models import Q, Min
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response

from medtour.guides.serializers import (
    ProgramSerializer, ProgramListSerializer, ProgramDetailSerializer,
    ProgramPlacesSerializer, ProgramInfoScheduleSerializer, ProgramReviewSerializer, ProgramServicesSerializer)
from medtour.guides.models import (
    Program, ProgramServices, ProgramPlaces, ProgramReview, ProgramInfoSchedule, ProgramPrice)


class ProgramReviewViewSet(viewsets.ModelViewSet):
    queryset = ProgramReview.objects.all()
    serializer_class = ProgramReviewSerializer
    http_method_names = ["get", "post"]
    filterset_fields = ["program_id"]

    @extend_schema(
        parameters=[OpenApiParameter(name="program_id", required=True, type=int)],
        responses={"200": ProgramReviewSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        program_id = request.query_params.get('program_id')  # noqa
        if not program_id:
            return Response(
                {
                    "message": _("Обязательный параметр program_id не указан.")},
                status=status.HTTP_400_BAD_REQUEST)
        return super().list(request, *args, **kwargs)


class ProgramViewSet(viewsets.ModelViewSet):
    queryset = Program.objects.prefetch_related("services", "excluded_services", "program_shots").select_related(
        "tour")
    serializer_class = ProgramSerializer
    filterset_fields = ["tour_id"]
    list_serializer_class = ProgramListSerializer
    retrieve_serializer_class = ProgramDetailSerializer

    @extend_schema(
        parameters=[OpenApiParameter(name="tour_id", required=True, type=int)],
        responses={"200": ProgramListSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        tour_id = request.query_params.get('tour_id')  # noqa
        if not tour_id:
            return Response(
                {
                    "message": _("Обязательный параметр tour_id не указан.")},
                status=status.HTTP_400_BAD_REQUEST)
        qs = self.get_queryset().filter(guide_id=tour_id, hide=False)[:24]
        serializer = self.list_serializer_class(qs, many=True)
        return Response(serializer.data)

    @extend_schema(
        responses={"200": ProgramDetailSerializer(many=False)}
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.retrieve_serializer_class(instance)
        return Response(serializer.data)


class ProgramManyViewWithoutPagination(generics.ListAPIView):
    queryset = Program.objects.all()
    serializer_class = ProgramListSerializer

    @extend_schema(summary="Получение много програм гидов по конкретным id",
                   parameters=[
                       OpenApiParameter(name="id__in", description="Введите id__in програм гидов", required=True)],
                   responses={'200': ProgramListSerializer(many=True)},
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


class ProgramPlacesAPIView(viewsets.ModelViewSet):
    queryset = ProgramPlaces.objects.all()
    serializer_class = ProgramPlacesSerializer
    filterset_fields = ["program_id"]


class ProgramInfoScheduleAPIView(viewsets.ModelViewSet):
    queryset = ProgramInfoSchedule.objects.all()
    serializer_class = ProgramInfoScheduleSerializer
    filterset_fields = ["program_id"]


class ProgramServicesViewset(viewsets.ModelViewSet):
    queryset = ProgramServices.objects.all()
    serializer_class = ProgramServicesSerializer
    filterset_fields = ["tour_id"]

    @extend_schema(
        parameters=[OpenApiParameter(name="tour_id", required=True, type=int)],
        responses={"200": ProgramServicesSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        guide_id = request.query_params.get('tour_id')  # noqa
        if not guide_id:
            return Response(
                {
                    "message": _("Обязательный параметр tour_id не указан.")},
                status=status.HTTP_400_BAD_REQUEST)
        return super().list(request, *args, **kwargs)


class ProgramPricesAPIView(viewsets.ModelViewSet):
    queryset = ProgramPrice.objects.all()
