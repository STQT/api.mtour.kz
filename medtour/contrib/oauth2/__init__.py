import requests

from urllib.parse import urlencode


class Oauth2Provider:
    """This Provider defaults for Google OAuth"""
    oauth2_url = "https://accounts.google.com/o/oauth2/auth?"  # HINT: "?" should be a setting this attribute
    provider_auth_url = "https://oauth2.googleapis.com/token"
    user_info_url = "https://openidconnect.googleapis.com/v1/userinfo"
    redirect_uri = None
    client_id = None
    client_secret = None
    scope = "email"
    fields = "email"

    @property
    def parameters(self) -> dict:
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            'scope': self.scope,
        }
        return params

    @classmethod
    def generate_redirect_url(cls):
        url = cls.oauth2_url + urlencode(cls().parameters)
        return url

    @classmethod
    def authorize_oauth2_server(cls, code: str):
        params = cls().parameters
        params['code'] = code
        params['grant_type'] = 'authorization_code'
        params['client_secret'] = cls.client_secret
        response = requests.post(cls.provider_auth_url, data=params)
        return response.json()

    @classmethod
    def retrieve_user_data(cls, token_data: dict):
        # Use the access token to retrieve user information
        userinfo_url = cls.user_info_url
        headers = {
            'Authorization': f'Bearer {token_data["access_token"]}',
        }
        try:
            response = requests.get(userinfo_url, headers=headers)
        except KeyError:
            raise OauthException
        return response.json()

    @classmethod
    def get_user_data(cls, code: str):
        user_json = cls.authorize_oauth2_server(code)
        return cls.retrieve_user_data(user_json)

    def get_validated_data(self, code):
        user_json = self.authorize_oauth2_server(code)
        data = self.retrieve_user_data(user_json)

        return {
            "id": data["id"],
            "email": data["email"],
            "first_name": data["first_name"],
            "last_name": data["last_name"],
            "picture": data["picture"]["url"],
        }


class OauthException(Exception):
    ...
