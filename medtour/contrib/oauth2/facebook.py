import requests
from django.conf import settings

from medtour.contrib.oauth2 import Oauth2Provider, OauthException


class FacebookOAuth(Oauth2Provider):
    oauth2_url = "https://www.facebook.com/dialog/oauth?"  # HINT: "?" should be a setting this attribute
    provider_auth_url = "https://graph.facebook.com/v17.0/oauth/access_token"
    user_info_url = "https://graph.facebook.com/me"

    redirect_uri = "https://dev.mtour.kz/oauth2/callback/facebook/"
    client_id = "3564887573798516"
    # client_secret = settings.OAUTH_FACEBOOK_SECRET
    client_secret = "55fde4a15b2c9026fa23b2112ba50bfc"
    fields = "first_name,email,last_name,picture"

    @classmethod
    def authorize_oauth2_server(cls, code):
        params = cls().parameters
        params['code'] = code
        params['client_secret'] = cls.client_secret
        response = requests.get(cls.provider_auth_url, params=params)
        return response.json()

    @classmethod
    def retrieve_user_data(cls, token_data):
        # Use the access token to retrieve user information
        userinfo_url = cls.user_info_url
        try:
            response = requests.get(userinfo_url, params={"access_token": token_data["access_token"],
                                                          "fields": cls.fields})
        except KeyError:
            raise OauthException
        return response.json()

    @classmethod
    def get_validated_data(cls, code):
        user_json = cls.authorize_oauth2_server(code)
        data = cls.retrieve_user_data(user_json)

        return {
            "id": data["id"],
            "email": data["email"],
            "first_name": data["first_name"],
            "last_name": data["last_name"],
            "picture": data["picture"]['data']["url"],
        }
