from rest_framework import status
from rest_framework.response import Response


def verification_code_name(code, validated_code, obj):
    if str(code) == str(validated_code):
        obj.is_verified = True
        obj.save()
        return True
    return False


def validate_password(obj, serializer):
    if serializer.data.get("new_password1") == serializer.data.get("new_password2"):  # noqa
        obj.object.set_password(serializer.data.get("new_password1"))
        obj.object.save()
        response = {
            'status': 'success',
            'code': status.HTTP_200_OK,
            'message': 'Password updated successfully',
            'data': []
        }
        return Response(response)


def check_is_authorized(obj):
    if isinstance(obj.request.user.id, int) is False:
        return Response(status=status.HTTP_401_UNAUTHORIZED, data={"message": "Unauthorized"})


def refresh_token_setter(response):
    if response.data.get('refresh'):  # noqa
        cookie_max_age = 3600 * 24 * 14  # 14 days
        response.set_cookie('refresh_token', response.data['refresh'], max_age=cookie_max_age, httponly=True)
        del response.data['refresh']
