from django.db.transaction import atomic
from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from medtour.contrib.serializers import ReadWriteSerializerMixin
from medtour.orders.serializers import WriteServiceCartSerializer, ServiceCartSerializer, PaymentSerializer
from medtour.orders.models import Payment, ServiceCart


class ServiceCartView(ReadWriteSerializerMixin, viewsets.ModelViewSet):
    """Корзина тура для проведения оплаты"""
    queryset = ServiceCart.objects.all()
    write_serializer_class = WriteServiceCartSerializer
    read_serializer_class = ServiceCartSerializer
    permission_classes = (IsAuthenticated,)
    filterset_fields = ["tour_id"]
    http_method_names = ["get", "post"]

    def list(self, request, *args, **kwargs):
        return Response({"error": _("Метод \"GET\" не разрешен.")},
                        status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @atomic
    def perform_create(self, serializer):
        serializer.save()

    def get_queryset(self):
        return ServiceCart.objects.filter(user=self.request.user).select_related(
            "tour", "user", "number"
        ).prefetch_related("service_count_packages", "service_count_packages")


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    http_method_names = ["get", "post", "patch", "put"]
    filterset_fields = ["user_id", "cart_id"]
    pagination_class = None
