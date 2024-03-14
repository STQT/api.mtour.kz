from rest_framework.views import APIView
from rest_framework.response import Response

from medtour.orders.models import Payment


class Kassa24CallbackView(APIView):
    serializer_class = None

    def post(self, request):  # noqa
        # Handle the callback request here
        # TODO: convert to async function
        data = request.data
        status = int(data.get('status'))
        pay_obj = Payment.objects.filter(cart_id=str(data.get("orderId")))

        if pay_obj.exists():
            pay_obj = pay_obj.first()

            reserv_qs = pay_obj.san_reservations if hasattr(pay_obj, "san_reservations") else None
            if reserv_qs:
                reserv_qs.update(paid=True if status == 1 else False)
                pay_obj.status = int(status) if status == 1 else 0
                pay_obj.save()
        # process the callback data, update the order status, etc.
        return Response(status=200)
