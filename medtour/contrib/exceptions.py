from rest_framework.exceptions import APIException
from rest_framework import status
from django.utils.translation import gettext_lazy as _


class ImATeapot(APIException):
    status_code = status.HTTP_418_IM_A_TEAPOT
    default_detail = _("I'm a teapot")
    default_code = 'imateapot'


class PaymentError(APIException):
    status_code = status.HTTP_402_PAYMENT_REQUIRED
    default_detail = _("Payment error. Please try again")
    default_code = 'payment_error'
