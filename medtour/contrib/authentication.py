from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _
from drf_spectacular.extensions import OpenApiAuthenticationExtension
from drf_spectacular.utils import OpenApiParameter
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
from rest_framework_simplejwt.settings import USER_SETTINGS, DEFAULTS, IMPORT_STRINGS, APISettings

User = get_user_model()
api_settings = APISettings(USER_SETTINGS, DEFAULTS, IMPORT_STRINGS)


class CachedJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        try:
            user_id = validated_token[api_settings.USER_ID_CLAIM]
            user = cache.get(f'user_{user_id}')
        except KeyError:
            raise InvalidToken(_("Token contained no recognizable user identification"))
        if user is not None:
            return user

        try:
            user = self.user_model.objects.get(**{api_settings.USER_ID_FIELD: user_id})
            cache.set(f'user_{user_id}', user, timeout=60 * 5)  # Store for 5 minutes
        except self.user_model.DoesNotExist:
            raise AuthenticationFailed(_("User not found"), code="user_not_found")

        if not user.is_active:
            raise AuthenticationFailed(_("User is inactive"), code="user_inactive")

        return user


class CachedJWTAuthenticationExtension(OpenApiAuthenticationExtension):
    name = 'jwt_cached_auth'
    target_class = 'medtour.contrib.authentication.CachedJWTAuthentication'

    def get_security(self, auto_schema, **kwargs):
        return [{"JWT Token": []}]

    def get_responses(self, auto_schema, **kwargs):
        return {
            "401": OpenApiParameter(
                name="WWW-Authenticate",
                in_=OpenApiParameter.HEADER,
                required=True,
                schema={"type": "string"},
                description="Authentication credentials were missing or incorrect.",
            ),
            "403": OpenApiParameter(
                name="WWW-Authenticate",
                in_=OpenApiParameter.HEADER,
                required=True,
                schema={"type": "string"},
                description="The authenticated user does not have sufficient permissions.",
            ),
        }

    def get_security_definition(self, auto_schema):
        return {
            "JWT Token": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            }
        }


CachedJWTAuthenticationStateExtension = CachedJWTAuthenticationExtension
