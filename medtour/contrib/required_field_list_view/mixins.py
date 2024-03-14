from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import mixins, status
from rest_framework.response import Response


class TourIdListModelMixin(mixins.ListModelMixin):
    """
    List a queryset.
    """

    @extend_schema(
        parameters=[OpenApiParameter(name="tour_id", required=True, type=int)])
    def list(self, request, *args, **kwargs):
        tour_id = request.query_params.get('tour_id')
        if not tour_id:
            return Response(
                {
                    "message": _("Обязательный параметр tour_id не указан.")},
                status=status.HTTP_400_BAD_REQUEST)
        return super().list(request, *args, **kwargs)


class TourNumberIdListModelMixin(mixins.ListModelMixin):
    """
    List a queryset.
    """

    @extend_schema(
        parameters=[OpenApiParameter(name="tour_number_id", required=True, type=int)])
    def list(self, request, *args, **kwargs):
        tour_id = request.query_params.get('tour_number_id')
        if not tour_id:
            return Response(
                {
                    "message": _("Обязательный параметр tour_number_id не указан.")},
                status=status.HTTP_400_BAD_REQUEST)
        return super().list(request, *args, **kwargs)
