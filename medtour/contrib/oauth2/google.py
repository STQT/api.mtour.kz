from urllib.parse import urlencode

from django.conf import settings

from medtour.contrib.oauth2 import Oauth2Provider


class GoogleOAuth(Oauth2Provider):
    redirect_uri = "http://localhost:3000/oauth2/callback/google/"
    client_id = "709802184819-g1mvf58k46l7fnev0g5rubd3ue8cj05m.apps.googleusercontent.com"
    client_secret = settings.OAUTH_GOOGLE_SECRET
    scope = "openid email profile"

    @classmethod
    def generate_redirect_url(cls):
        params = cls().parameters
        params['response_type'] = 'code'
        url = cls.oauth2_url + urlencode(params)
        return url

    @classmethod
    def get_validated_data(cls, code):
        user_json = cls.authorize_oauth2_server(code)
        data = cls.retrieve_user_data(user_json)
        return {
            "id": data["sub"],
            "email": data["email"],
            "picture": data['picture'],
            "first_name": data["given_name"],
            "last_name": data["family_name"],
        }
