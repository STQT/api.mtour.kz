from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status
from rest_framework.response import Response

from medtour.contrib.exceptions import ImATeapot
from medtour.contrib.serializers import ReadWriteSerializerMixin
from medtour.contrib.soft_delete_model import SoftDeleteModelViewSet
from medtour.tourpackages.serializers import ListPackageSerializer, WriteTourPackageSerializer, \
    RetrievePackageSerializer
from medtour.tourpackages.models import TourPackages, TourPackagesServices


class TourPackagesView(ReadWriteSerializerMixin, SoftDeleteModelViewSet):  # noqa F405
    """Тур checkup пакеты"""
    queryset = TourPackages.objects.all()  # prefetch_related("tour")  # TODO: filter by tour_is_moderated
    read_serializer_class = ListPackageSerializer
    retrieve_serializer_class = RetrievePackageSerializer
    write_serializer_class = WriteTourPackageSerializer
    pagination_class = None
    filterset_fields = {
        "id": ["exact", "in"],
        "tour_id": ["exact"],
    }

    def get_queryset(self):
        if self.request.query_params.get("id__in") == "":
            raise ImATeapot
        qs = super().get_queryset()
        if self.action == "list":
            qs = qs.filter(is_deleted=False)
        return qs

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            """ Валидация ПОСТ запроса"""
            validated_data = serializer.validated_data
            package_services = validated_data.pop('package_services', "")
            if type(package_services) is str:  # noqa F405
                package_services = package_services.split(",")
            instance = serializer.save()
            TourPackagesServices.objects.bulk_create(
                [
                    TourPackagesServices(package=instance, title=service)
                    for service in package_services
                ]
            )
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        parameters=[OpenApiParameter(name="tour_id", required=True, type=int)])
    def list(self, request, *args, **kwargs):
        tour_id = self.request.query_params.get('tour_id')
        if not tour_id:
            return Response(
                {
                    "message": _("Обязательный параметр tour_id не указан.")},
                status=status.HTTP_400_BAD_REQUEST)
        return super().list(request, *args, **kwargs)
