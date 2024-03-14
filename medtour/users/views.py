from dj_rest_auth.serializers import PasswordChangeSerializer
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.db import transaction
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django.views.generic import DetailView, RedirectView, UpdateView

from drf_spectacular.utils import extend_schema, OpenApiParameter, extend_schema_view  # noqa F405
from phone_auth.models import EmailAddress, PhoneNumber
from rest_framework import mixins, permissions, status, viewsets, generics
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, NotAuthenticated
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.serializers import TokenRefreshSerializer, TokenBlacklistSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenViewBase, TokenBlacklistView

from medtour.contrib.pagination import StandardResultsSetPagination
from medtour.notifications.models import Notification
from medtour.notifications.serializers import NotificationSerializer
from medtour.orders.models import Payment
from medtour.users.serializers import (TokenObtainLifetimeSerializer, TokenRefreshLifetimeSerializer,
                                       RegisterOrgSerializer, OrganizationSerializer, LogoutSerializer,
                                       ProfileSerializer, CountrySerializer,
                                       RegionSerializer, UserReadSerializer, EmailAddressSerializer,
                                       PhoneNumberSerializer, ResponseRegisterSerializer,
                                       PayHistoryHistorySerializer, ResetPasswordSerializer, UserVerifySerializer,
                                       PayHistoryHistoryDetailSerializer, PasswordResetChangeSerializer,
                                       PartUserCreateSerializer, CitySerializer,
                                       FirstPageCountriesSerializer)
from medtour.users.serializers import UserSerializer, CodeSerializer, RegisterUserSerializer
from medtour.users.validators import (verification_code_name, check_is_authorized, validate_password,
                                      refresh_token_setter)
from medtour.users.models import Organization, Person, Country, Region, ActivateCode, RestoreCode, City
from medtour.users.permissions import IsPeople
from medtour.utils import random_username

User = get_user_model()


class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [AllowAny]
    filterset_fields = ["user_id"]

    @action(detail=False)
    def me(self, request):
        check_is_authorized(self)
        queryset = Organization.objects.filter(user=request.user).prefetch_related("user").first()
        serializer = self.get_serializer(queryset, many=False)
        return Response(serializer.data)


class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = ProfileSerializer
    filterset_fields = ["user_id"]
    permission_classes = [permissions.IsAuthenticated, IsPeople]

    @action(detail=False)
    def me(self, request):
        check_is_authorized(self)
        queryset = Person.objects.filter(user=request.user).prefetch_related("user").first()
        serializer = self.get_serializer(queryset, many=False)
        return Response(serializer.data)

    @extend_schema(summary="История покупок", description="Вывод всех приобретенных туров пользователя",
                   responses={200: PayHistoryHistorySerializer(many=True)})
    @action(detail=False)
    def payHistory(self, request):  # noqa
        if isinstance(self.request.user.id, int) is False:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data={"message": "Unauthorized"})
        queryset = Payment.objects.filter(
            user=request.user
        ).prefetch_related("user")
        self.pagination_class = StandardResultsSetPagination  # TODO: need to support
        page = self.paginate_queryset(queryset)
        serializer = PayHistoryHistorySerializer
        if page is not None:
            serializer = serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = serializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(summary="История покупок", description="Вывод всех приобретенных туров пользователя",
                   responses={200: PayHistoryHistoryDetailSerializer},
                   parameters=[OpenApiParameter("payHistoryId", int, required=True)],
                   )
    @action(detail=False)
    def payHistoryDetail(self, request):  # noqa
        if isinstance(self.request.user.id, int) is False:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data={"message": "Unauthorized"})
        obj = generics.get_object_or_404(Payment, id=self.request.query_params.get('payHistoryId'))
        serializer = PayHistoryHistoryDetailSerializer(obj, many=False)
        return Response(serializer.data)


class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  viewsets.GenericViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.prefetch_related(
        "emailaddress_set__user", "phonenumber_set__user"
    ).select_related("people", "organization")

    def get_queryset(self, *args, **kwargs):
        if isinstance(self.request.user.id, int) is False:
            return self.queryset.none()
        return self.queryset

    @extend_schema(summary="Для полного просмотра имеется /v1/organizations/me и /v1/profile/me",
                   description="Не используйте /me для просмотра подробностей",
                   responses=UserReadSerializer)
    @action(detail=False)
    def me(self, request):
        if isinstance(self.request.user.id, int) is False:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data={"message": "Unauthorized"})
        serializer = UserReadSerializer(self.request.user, context={"request": request})
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class CountryView(mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer


class RegionView(mixins.ListModelMixin,
                 viewsets.GenericViewSet):
    queryset = Region.objects.all()
    filterset_fields = ["country_id"]
    serializer_class = RegionSerializer


class CityView(mixins.ListModelMixin,
               viewsets.GenericViewSet):
    queryset = City.objects.all()
    filterset_fields = ["region_id"]
    serializer_class = CitySerializer


class MainPageCountryView(mixins.ListModelMixin,
                          viewsets.GenericViewSet):
    queryset = Country.objects.all()  # .filter(regions__cities__is_first_page=True).prefetch_related('regions__cities')
    serializer_class = FirstPageCountriesSerializer

    def get_queryset(self):
        return super().get_queryset().prefetch_related('regions__cities')

    # def get_serializer_context(self):
    #     context = super().get_serializer_context()
    #     context['is_first_page_cities'] = self.queryset.prefetch_related(
    #         'regions__cities').filter(regions__cities__is_first_page=True).distinct()
    #     print(context)
    #     return context


class TokenObtainPairView(TokenViewBase):
    """
        Return JWT tokens (access and refresh) for specific user based on username and password.
    """
    serializer_class = TokenObtainLifetimeSerializer


class TokenRefreshView(TokenViewBase):
    """
        Renew tokens (access and refresh) with new expire time based on specific user's access token.
    """
    serializer_class = TokenRefreshLifetimeSerializer


class PasswordChangeView(generics.UpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = PasswordChangeSerializer
    throttle_scope = 'dj_rest_auth'

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()  # noqa
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)

            validate_password(self, serializer)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetChangeView(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = PasswordResetChangeSerializer
    throttle_scope = 'dj_rest_auth'

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()  # noqa
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            validate_password(self, serializer)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetActiveView(generics.GenericAPIView):
    """Верификация кода для восстановления пароля"""
    serializer_class = CodeSerializer
    permission_classes = [AllowAny]

    @extend_schema(responses={200: UserVerifySerializer})
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            data = serializer.validated_data  # noqa
            user = data.get('userId')
            num = RestoreCode.objects.filter(user=user)
            if num.exists():  # noqa
                num = num.first()
            else:
                raise NotAuthenticated(
                    "Ваша ссылка устарела, пожалуйста попробуйте переотправить код подтверждения")
            email_qs = EmailAddress.objects.filter(user=user)
            phone_qs = PhoneNumber.objects.filter(user=user)
            verified = 0
            token = None
            if email_qs.exists():  # noqa
                email_obj = email_qs.first()
                result = verification_code_name(num.number, data.get("hashCode"), email_obj)
                if result is not False:
                    token = self.get_tokens_for_user(email_obj.user).get('access')
                    RestoreCode.objects.filter(user=email_obj.user).delete()
                    verified += 1

            if phone_qs.exists():  # noqa
                phone_obj = phone_qs.first()
                result = verification_code_name(num.number, data.get("hashCode"), phone_obj)
                if result is not False:
                    token = self.get_tokens_for_user(phone_obj.user).get('access')
                    RestoreCode.objects.filter(user=phone_obj.user).delete()
                    verified += 1
            if verified == 0:
                raise NotAuthenticated("Неправильный код попробуйте заново запросить код подтверждения.")
            return Response({"message": _("Вы можете восстановить аккаунт."), 'token': token},
                            status=status.HTTP_200_OK)
        return Response({"detail": _('Неверная ссылка')}, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_tokens_for_user(user):
        refresh = RefreshToken.for_user(user)
        return {'refresh': str(refresh), 'access': str(refresh.access_token)}


class RegisterUserAPIView(generics.GenericAPIView):
    """Регистрация простого смертного пользователя"""
    serializer_class = RegisterUserSerializer
    response_serialiizer = ResponseRegisterSerializer
    permission_classes = (AllowAny,)

    @extend_schema(responses=ResponseRegisterSerializer)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        response_serializer = self.response_serialiizer
        if serializer.is_valid(raise_exception=True):
            """ Валидация ПОСТ запроса"""
            validated_data = serializer.validated_data
            phone = validated_data.pop('phone', None)
            email = validated_data.pop('email', None)
            country = validated_data.pop('country', 'kz')
            is_organization = validated_data.get('is_organization', False)
            # username randomizer
            username = random_username(country, email, phone, is_organization)
            validated_data.update({"username": username})

            errors = {}
            if email is None and phone is None:
                errors["phone"] = [_('Введите пожалуйста email или телефонный номер'), ]
                errors["email"] = [_('Введите пожалуйста email или телефонный номер'), ]

            if email is not None:
                if EmailAddress.objects.filter(email__iexact=email).exists():
                    errors["email"] = [_("Email почта уже существует")]
            if phone is not None:
                if PhoneNumber.objects.filter(phone=phone).exists():
                    errors["phone"] = [_("Телефонный номер уже существует")]

            if User.objects.filter(username=username).count() > 0:
                errors["detail"] = [_("Пользователь с вашими введенными данными уже зарегистрированы в системе")]
            if errors:
                raise ValidationError(errors)
            user_creations = serializer.save()
            if not user_creations:
                raise ValidationError(detail=_("Пользователь не зарегистрировался возможно уже существует"))
            """Отправка кода пользователю"""  # TODO: convert to function after
            user = User.objects.filter(pk=serializer.data.get('id')).first()
            # TODO: celery
            if phone:
                PhoneNumber.objects.create(user=user, phone=phone)
            if email:
                EmailAddress.objects.create(user=user, email=email)
            code = ActivateCode.objects.create(user=user)

            # TODO: celery
            message = _('Ссылка: {}/activate/?userId={}&code={}').format(
                Site.objects.get_current().domain,
                user.pk,
                str(code.number)
            )
            if email:
                user.send_message_user(subject=settings.DEFAULT_FROM_EMAIL,
                                       from_email=settings.DEFAULT_FROM_EMAIL,
                                       message=message,
                                       emails=[email])
            else:
                user.send_message_user(subject=settings.DEFAULT_FROM_EMAIL,
                                       message=message,
                                       phone=str(phone))
            return Response(response_serializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterOrgAPIView(RegisterUserAPIView):
    """Регистрация организации, требуется отправить либо телефонный номер либо эмейл

    Обязательно указать юзернейм для платежной системы
    """
    serializer_class = RegisterOrgSerializer


class VerifyCodeView(generics.GenericAPIView):
    """Верификация кода отправленный на почту или в мобильный телефон"""
    serializer_class = CodeSerializer
    permission_classes = [AllowAny]

    @extend_schema(responses={200: UserVerifySerializer})
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            data = serializer.validated_data  # noqa
            user = data.get('userId')
            num = ActivateCode.objects.filter(user=user)
            if num.exists():  # noqa
                num = num.first()
            else:
                raise NotAuthenticated("Ваша ссылка устарела, пожалуйста попробуйте переотправить код подтверждения")
            email_qs = EmailAddress.objects.filter(user=user)
            phone_qs = PhoneNumber.objects.filter(user=user)
            verified = 0
            token = None
            if email_qs.exists():  # noqa
                email_obj = email_qs.first()
                result = verification_code_name(num.number, data.get("hashCode"), email_obj)
                if result is not False:
                    token = self.get_tokens_for_user(email_obj.user).get('access')
                    ActivateCode.objects.filter(user=email_obj.user).delete()
                    verified += 1

            if phone_qs.exists():  # noqa
                phone_obj = phone_qs.first()
                result = verification_code_name(num.number, data.get("hashCode"), phone_obj)
                if result is not False:
                    token = self.get_tokens_for_user(phone_obj.user).get('access')
                    ActivateCode.objects.filter(user=phone_obj.user).delete()
                    verified += 1
            if verified == 0:
                raise NotAuthenticated("Неправильный код попробуйте заново запросить код подтверждения")
            return Response({"message": _("Аккаунт успешно подтверждён."), 'token': token}, status=status.HTTP_200_OK)
        return Response({"detail": _('Неверная ссылка')}, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_tokens_for_user(user):
        refresh = RefreshToken.for_user(user)
        return {'refresh': str(refresh), 'access': str(refresh.access_token)}


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LogoutSerializer

    def post(self, request, *args, **kwargs):  # noqa
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except:  # noqa
            return Response(status=status.HTTP_400_BAD_REQUEST)


class ResetPassword(APIView):
    permission_classes = [AllowAny]
    serializer_class = ResetPasswordSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            """ Валидация ПОСТ запроса"""
            validated_data = serializer.validated_data
            phone = validated_data.pop('phone', None)
            email = validated_data.pop('email', None)
            user = None
            errors = {}
            if email is None and phone is None:
                errors["phone"] = [_('Введите пожалуйста email или телефонный номер'), ]
                errors["email"] = [_('Введите пожалуйста email или телефонный номер'), ]

            if email is not None:
                email_obj = EmailAddress.objects.filter(email__iexact=email)
                if email_obj.exists():
                    user = email_obj.first().user
                else:
                    errors['email'] = [_("Не найден пользователь с такой почтой")]

            if phone is not None:
                phone_obj = PhoneNumber.objects.filter(phone=phone)
                if phone_obj.exists():
                    user = phone_obj.first().user
                else:
                    errors["phone"] = [_("Не найден пользователь с таким номером")]
            if user is None:
                errors["user"] = [_('Не найден никакой пользователь по указанным данным'), ]
            if errors:
                raise ValidationError(errors)
            code = RestoreCode.objects.create(user=user)
            """Отправка кода пользователю"""  # TODO: convert to function after
            # TODO: celery
            message = _('Ссылка для восстановления: {}/reset-password/?userId={}&code={}').format(
                Site.objects.get_current().domain,
                user.pk,
                str(code.number)
            )
            if email:
                user.send_message_user(subject=settings.DEFAULT_FROM_EMAIL,
                                       from_email=settings.DEFAULT_FROM_EMAIL,
                                       message=message,
                                       emails=[email])
            else:
                user.send_message_user(subject=settings.DEFAULT_FROM_EMAIL,
                                       message=message,
                                       phone=str(phone))
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CookieTokenRefreshSerializer(TokenRefreshSerializer):
    refresh = None

    def validate(self, attrs):
        attrs['refresh'] = self.context['request'].COOKIES.get('refresh_token')
        if attrs['refresh']:
            return super().validate(attrs)
        else:
            raise InvalidToken('No valid token found in cookie \'refresh_token\'')


class CookieTokenLogoutSerializer(TokenBlacklistSerializer):
    refresh = None

    def validate(self, attrs):
        attrs['refresh'] = self.context['request'].COOKIES.get('refresh_token')
        if attrs['refresh']:
            return super().validate(attrs)
        else:
            raise InvalidToken('No valid token found in cookie \'refresh_token\'')


class CookieTokenObtainPairView(TokenObtainPairView):
    def finalize_response(self, request, response, *args, **kwargs):
        response.set_cookie(
            'mtour', "marketplace", max_age=86400, httponly=True,
        )
        refresh_token_setter(response)
        return super().finalize_response(request, response, *args, **kwargs)


class CookieTokenRefreshView(TokenRefreshView):
    def finalize_response(self, request, response, *args, **kwargs):
        response.set_cookie('sharik', "darik")
        refresh_token_setter(response)
        return super().finalize_response(request, response, *args, **kwargs)

    serializer_class = CookieTokenRefreshSerializer


class CookieTokenLogoutView(TokenBlacklistView):
    serializer_class = CookieTokenLogoutSerializer


class EmailAddressView(viewsets.ModelViewSet):
    queryset = EmailAddress.objects.all()
    serializer_class = EmailAddressSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["user_id"]

    @extend_schema(
        description="Вывод всех email пользователя по user_id",
        parameters=[OpenApiParameter("user_id", int, required=True)]
    )
    def list(self, request, *args, **kwargs):
        user_id = self.request.query_params.get('user_id', None)
        if not user_id:
            return Response({"message": _("Обязательный параметр не указан.")},
                            status=status.HTTP_404_NOT_FOUND)
        return super().list(request, *args, **kwargs)


class PhoneNumberView(viewsets.ModelViewSet):
    queryset = PhoneNumber.objects.all()
    serializer_class = PhoneNumberSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["user_id"]

    @extend_schema(
        description="Вывод всех телефонных номеров пользователя по user_id",
        parameters=[OpenApiParameter("user_id", int, required=True)]
    )
    def list(self, request, *args, **kwargs):
        user_id = self.request.query_params.get('user_id', None)
        if not user_id:
            return Response({"message": _("Обязательный параметр не указан.")},
                            status=status.HTTP_404_NOT_FOUND)
        return super().list(request, *args, **kwargs)


class CreateUserView(APIView):
    serializer_class = PartUserCreateSerializer

    @transaction.atomic
    def post(self, request):
        serializer = PartUserCreateSerializer(data=request.data)
        if serializer.is_valid():
            # Generate a random password
            password = get_random_string(length=4)
            phone = serializer.validated_data['phone']
            first_name = serializer.validated_data['first_name']
            last_name = serializer.validated_data['last_name']
            country = serializer.validated_data.pop('country', 'kz')

            errors = {}
            if str(phone).replace('+', '').isnumeric() is False:
                errors["phone"] = [_("Введите корректный телефонный номер")]
            if PhoneNumber.objects.filter(phone=phone).exists():
                errors["phone"] = [_("Телефонный номер уже существует")]

            username = random_username(country, str(phone))
            if User.objects.filter(username=username).count() > 0:
                errors["detail"] = [_("Пользователь с вашими введенными данными уже зарегистрированы в системе")]
            if errors:
                raise ValidationError(errors)
            # Create the user with the provided email and random password
            user = User.objects.create_user(username=username, password=password,
                                            first_name=first_name, last_name=last_name)
            PhoneNumber.objects.create(user=user, phone=phone)
            Person.objects.create(user=user, first_name=first_name, last_name=last_name)

            # Send the login credentials to the user's email
            message = (_('Ваш пароль: {password}').format(password=password))  # noqa
            try:
                response_text = user.send_message_user(subject=settings.DEFAULT_FROM_EMAIL,
                                                       message=message,
                                                       phone=str(phone))
                if response_text[1] <= "0":
                    transaction.set_rollback(True)
                    raise ValidationError({"phone": [_("Сообщение не отправлено")]})
            except TypeError as e:
                transaction.set_rollback(True)
                raise ValidationError({"detail": [e]})
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)


# Django rendering home page
class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    slug_field = "username"
    slug_url_kwarg = "username"


user_detail_view = UserDetailView.as_view()


class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    fields = ["name"]
    success_message = _("Information successfully updated")

    def get_success_url(self):
        assert (
            self.request.user.is_authenticated
        )  # for mypy to know that the user is authenticated
        return self.request.user.get_absolute_url()

    def get_object(self):
        return self.request.user


user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self):
        return reverse("users:detail", kwargs={"username": self.request.user.username})


user_redirect_view = UserRedirectView.as_view()


class NotificationViewSet(mixins.ListModelMixin,
                          mixins.RetrieveModelMixin,
                          viewsets.GenericViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.queryset.filter(user=self.request.user,
                                                              read=self.request.query_params.
                                                              get('read', False)), many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        self.queryset.filter(pk=kwargs['pk']).update(read=True)
        notification = self.queryset.get(pk=kwargs['pk'])
        serializer = NotificationSerializer(notification)
        return Response(serializer.data)
