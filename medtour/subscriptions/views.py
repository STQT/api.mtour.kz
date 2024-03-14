from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from medtour.subscriptions.serializers import TourSubscribeSerializer, SubscribePricesSerializer, \
    CreateSubscribeSerializer
from medtour.subscriptions.models import TourSubscribe, SubscribePrice


class TourSubscribeViewSet(viewsets.ModelViewSet):
    queryset = TourSubscribe.objects.all()
    serializer_class = TourSubscribeSerializer
    create_serializer_class = CreateSubscribeSerializer
    filterset_fields = "tour_id",
    http_method_names = ["post", "get"]

    def get_serializer_class(self):
        if self.action == 'create':
            return self.create_serializer_class
        return self.serializer_class

    @extend_schema(
        description="Retrieve a list of instances of the model",
        parameters=[OpenApiParameter('tour_id', required=True)]
    )
    def list(self, request, *args, **kwargs):
        missing_filters = set(self.filterset_fields) - set(request.query_params.keys())
        if missing_filters:
            return Response({"error": _("Missing required filters: {}").format(', '.join(missing_filters))},
                            status=status.HTTP_400_BAD_REQUEST)
        return super().list(request, *args, **kwargs)

    @extend_schema(responses={'200': SubscribePricesSerializer(many=True)})
    @action(detail=False)
    def subscribe_prices(self, request, *args, **kwargs):
        qs = SubscribePrice.objects.filter(is_actual=True)
        serializer = SubscribePricesSerializer(qs, many=True)
        return Response(serializer.data)
