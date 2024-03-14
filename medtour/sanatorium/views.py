from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from medtour.contrib.exceptions import ImATeapot
from medtour.contrib.soft_delete_model import SoftDeleteModelViewSet
from medtour.sanatorium.serializers import ReservationsSerializer, ReservationsCheckSerializer
from medtour.sanatorium.models import Reservations
from medtour.users.serializers import ActivateCodeSerializer
from medtour.users.models import ActivateCode
from medtour.utils.constants import ReservationApproveStatusChoices
from medtour.utils.send_mail import *

User = get_user_model()


class ReservationsView(SoftDeleteModelViewSet):
    """Резервирующим может быть и юрлицо и физлицо."""
    queryset = Reservations.objects.all()  # .prefetch_related("tour", "number_cabinets__tour_number",
    #                 "number", "number__tour", "partner__user")
    serializer_class = ReservationsSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["tour_id"]
    list_select_related = ("tour__org",)
    list_prelated_tuple = ("reservations_services",)

    def get_queryset(self):
        if not hasattr(self.request.user, 'organization'):
            raise PermissionDenied
        qs = self.queryset
        query = Q(tour__org=self.request.user.organization) # noqa
        if self.action == "list":
            query.add(Q(tour_id=self.request.query_params.get('tour_id')), Q.OR)
            return qs.filter(query).prefetch_related(
                *self.list_prelated_tuple
            ).select_related(*self.list_select_related)
        return qs.filter(query).select_related("tour__org")

    def get_permissions(self):
        if self.action == "check":
            return AllowAny(),
        return [permission() for permission in self.permission_classes]

    def get_serializer(self, *args, **kwargs):
        if self.action == "check":
            return ReservationsCheckSerializer
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    @extend_schema(summary="Количество свободных туров",
                   parameters=[
                       OpenApiParameter(name="daterange",
                                        description="Чтобы вывести укажите промежуток дат в виде"
                                                    "?daterange=YYYY-MM-DD,YYYY-MM-DD",
                                        required=True),
                       OpenApiParameter(name="number",
                                        description="Введите ID номера который нужно будет проверить",
                                        required=True)
                   ]
                   )
    @action(detail=False)
    def check(self, request, *args, **kwargs):
        daterange = request.query_params.get('daterange')  # noqa F405
        number = request.query_params.get('number')
        if not daterange or not number:
            return Response({"message": _("Обязательный параметр daterange или number не указан.")},
                            status=status.HTTP_400_BAD_REQUEST)
        start, end = daterange.split(',')
        if (start is None) or (end is None):
            raise ValidationError(detail=_("Не введён промежуток времен"))
        if start > end:
            raise ImATeapot(detail=_("Вы ввели дату поиска наоборот, перепроверьте пожалуйста"))

        count = Reservations.get_empty_cabinets(start, end, number).count()
        serializer = ReservationsCheckSerializer({"count": count}, many=False)
        return Response(serializer.data)

    @extend_schema(summary="Вывод броней",
                   parameters=[
                       OpenApiParameter(name="daterange",
                                        description="Чтобы вывести укажите промежуток дат в виде"
                                                    "?daterange=YYYY-MM-DD,YYYY-MM-DD или MM/DD/YYYY,MM/DD/YYYY",
                                        required=True),
                       OpenApiParameter(name="tour_id",
                                        description="Вывести все брони тура (с сайта, с ресепшна",
                                        required=True)
                   ])
    def list(self, request, *args, **kwargs):
        daterange = request.query_params.get('daterange')
        if daterange is None:
            raise ValidationError(detail=_("Пожалуйста введите daterange"))
        start, end = daterange.split(',')
        if (start is None) or (end is None):
            raise ValidationError(detail=_("Не введён промежуток времен"))
        if start > end:
            raise ImATeapot(detail=_("Вы ввели дату поиска наоборот, перепроверьте пожалуйста"))
        try:
            queryset = self.get_queryset().filter(
                reservation_date__overlap=(start, end)
            )
        except Exception as e:
            raise ValidationError(detail=_("Ошибка {}".format(e)))

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class SendConfirmationCodeView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = None

    def post(self, request, pk): # noqa
        reservation = Reservations.objects.filter(id=pk)
        if reservation.exists():
            reservation = reservation.first()
            user = User.objects.get(id=reservation.reservator_id)
            code = ActivateCode.objects.regenerate_otp(user_id=reservation.reservator_id)
            user.send_message_user(_("MTour.kz код подтверждения"),
                                   _("Код подтверждения: {code}").format(code=code.number))
            reservation.approved_status = ReservationApproveStatusChoices.SENT
            reservation.save()
            return Response({'message': _('Код подтверждения успешно отправлено')}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": _("Нет такой брони")}, status=status.HTTP_400_BAD_REQUEST)


class ValidateConfirmationCodeView(APIView):
    permission_classes = [AllowAny]
    serializer_class = ActivateCodeSerializer

    def post(self, request, pk):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            reservation = Reservations.objects.filter(id=pk)
            if reservation.exists():
                reservation = reservation.first()
                user = User.objects.get(id=reservation.reservator_id)
                code = data['number']
                if ActivateCode.objects.validate_otp(user=user, otp=code):
                    reservation.approved_status = ReservationApproveStatusChoices.APPROVED
                    reservation.save()
                    return Response({'message': _('Код подтвержден')}, status=status.HTTP_200_OK)
                else:
                    Response({'detail': _('Код подтверждения не верный')}, status=status.HTTP_406_NOT_ACCEPTABLE)
            else:
                return Response({"detail": _("Нет такой брони")}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
