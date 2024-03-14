import base64

import requests
from django.conf import settings
from django.urls import reverse


class PaymentApi:
    kassa24_url = 'https://ecommerce.pult24.kz/payment/create'

    def __init__(self, login: str, password: str):
        self.login = login
        self.credentials = login + ":" + password
        self.credentials_bytes = self.credentials.encode('ascii')
        self.base64_credentials = base64.b64encode(self.credentials_bytes).decode('ascii')
        self.headers = {'Authorization': 'Basic ' + self.base64_credentials}

    def create_payment(self, amount: int,
                       service_cart_id: int = None,
                       email: str = None,
                       phone: str = None
                       ) -> (str, bool):
        # Set up the login credentials

        data = {
            "amount": amount * 100,
            "merchantId": self.login,
            "callbackUrl": settings.MAIN_SITE_URL + reverse("v1:payment-callbacks:kassa24"),
            "successUrl": "{}/payment?status=success&cartId={}".format(settings.MAIN_SITE_URL, str(service_cart_id)),
            "failUrl": "{}/payment?status=fail".format(settings.MAIN_SITE_URL),
            "customerData": {
                "email": email,
                "phone": phone
            }
        }
        if service_cart_id:
            data['orderId'] = str(service_cart_id)

        # Make the request
        response = requests.post(self.kassa24_url,
                                 headers=self.headers,
                                 json=data)
        response_text = response.text
        if response.status_code == 201:
            return response.json()['url'], False
        elif settings.DEBUG is False:
            try:
                from sentry_sdk import capture_message
                capture_message("kassa24 error: ", response_text)
            except ImportError:
                ...

# print(PaymentApi("14141564717596838", "JAKN3fTs1yw15W8k9QBY").create_payment(1555, 142424))
