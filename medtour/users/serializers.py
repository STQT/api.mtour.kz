import logging

from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.forms import SetPasswordForm
from django.db.utils import IntegrityError
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from phone_auth.models import EmailAddress, PhoneNumber
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from medtour.contrib.drf_serializer_cache import SerializerCacheMixin
from medtour.orders.models import Payment
from medtour.tours.models import Tour
from medtour.users.models import Country, Region, ActivateCode, City
from medtour.users.models import Organization, Person, OrganizationCategory
from medtour.utils.constants import OrgTypeChoice

User = get_user_model()


class EmailAddressSerializer(serializers.ModelSerializer):
    is_verified = serializers.BooleanField(read_only=True)

    class Meta:
        model = EmailAddress
        fields = "__all__"


class PhoneNumberSerializer(serializers.ModelSerializer):
    is_verified = serializers.BooleanField(read_only=True)

    class Meta:
        model = PhoneNumber
        fields = "__all__"


class UserSerializer(SerializerCacheMixin, serializers.ModelSerializer):
    email = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()

    @extend_schema_field(PhoneNumberSerializer)
    def get_phone(self, obj):
        if not obj.phone_obj:
            return None
        serializer = PhoneNumberSerializer(obj.phone_obj, many=False, allow_null=True)
        serializer.bind("*", self)
        return serializer.data

    @extend_schema_field(EmailAddressSerializer)
    def get_email(self, obj):
        if not obj.email_obj:
            return None
        serializer = EmailAddressSerializer(obj.email_obj, many=False, allow_null=True)
        serializer.bind("*", self)
        return serializer.data

    class Meta:
        model = User
        fields = ["id", "username", "is_organization", "email", "phone"]


class OrganizationCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationCategory
        fields = "__all__"


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = "__all__"


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = "__all__"


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        exclude = ("is_first_page", "slug")


class FirstPageCitiesSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField(read_only=True)

    @extend_schema_field(OpenApiTypes.STR)
    def get_type(self, obj):
        return 'city'

    class Meta:
        model = City
        fields = ("type", "name", "slug")


class FirstPageCountriesSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField(read_only=True)
    cities = serializers.SerializerMethodField(read_only=True)

    # cities = FirstPageCitiesSerializer(many=True, read_only=True, source='cities')

    @extend_schema_field(OpenApiTypes.STR)
    def get_type(self, obj):
        return 'country'

    def get_cities(self, obj):
        regions = obj.regions
        if regions.exists():
            return FirstPageCitiesSerializer(
                regions.first().cities.filter(is_first_page=True).only("name", "slug"), many=True).data
        return []

    class Meta:
        model = Country
        fields = ('type', 'name', 'cities')


class ToursOnOrganizationSerializer(serializers.ModelSerializer):
    category_name = serializers.StringRelatedField(source="category.title", allow_null=True)
    region = RegionSerializer(read_only=True)
    country = CountrySerializer(read_only=True)

    class Meta:
        model = Tour
        fields = ("id", "title", "category_name", "category", "region", "country")


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = "__all__"


class OrganizationReadSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.username")
    category = serializers.StringRelatedField(read_only=True, required=False)

    # country = serializers.CharField(read_only=True, required=False, source="country.name") # REMOVED
    # region = serializers.CharField(read_only=True, required=False, source="region.name") # REMOVED

    class Meta:
        model = Organization
        fields = "__all__"


class ProfileSerializer(serializers.ModelSerializer):
    country = CountrySerializer(read_only=True)
    region = RegionSerializer(read_only=True)

    class Meta:
        model = Person
        fields = "__all__"


class UserReadSerializer(serializers.ModelSerializer):
    client = ProfileSerializer(many=False, read_only=True)
    partner = OrganizationSerializer(many=False, read_only=True)
    email = EmailAddressSerializer(read_only=True, allow_null=True)
    phone = PhoneNumberSerializer(read_only=True, allow_null=True)
    userId = serializers.IntegerField(read_only=True)
    tours = ToursOnOrganizationSerializer(many=True, read_only=True)
    guide = serializers.IntegerField(read_only=True, allow_null=True)
    pick = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "is_organization", "client", "partner", "email", "phone",
                  "userId", "tours", "guide", "pick"]

    def to_representation(self, instance):
        data = super().to_representation(instance)  # TODO: Need to optimization
        data["tours"] = []
        data["userId"] = instance.id
        data["pick"] = instance.pick
        if instance.email_obj:
            data["email"] = EmailAddressSerializer(instance.email_obj, many=False, allow_null=True).data
        if instance.phone_obj:
            data["phone"] = PhoneNumberSerializer(instance.phone_obj, many=False, allow_null=True).data
        if hasattr(instance, "people"):
            data["client"] = ProfileSerializer(instance.people).data
        elif hasattr(instance, "organization"):
            data["partner"] = OrganizationSerializer(instance.organization).data
            data["tours"] = ToursOnOrganizationSerializer(instance.organization.tours.filter(is_deleted=False),
                                                          many=True).data
        return data


class TokenObtainLifetimeSerializer(TokenObtainPairSerializer):
    client = ProfileSerializer(many=False, read_only=True)
    partner = OrganizationSerializer(many=False, read_only=True)
    userId = serializers.IntegerField(read_only=True)
    access = serializers.CharField(read_only=True)
    lifetime = serializers.IntegerField(read_only=True)
    tours = ToursOnOrganizationSerializer(many=True, read_only=True)
    guide = serializers.IntegerField(read_only=True, allow_null=True)
    email = EmailAddressSerializer(read_only=True)
    phone = PhoneNumberSerializer(read_only=True)

    # def validate(self, attrs):
    #     authenticate_kwargs = {
    #         self.username_field: attrs[self.username_field],
    #         'password': attrs['password'],
    #     }
    #     try:
    #         authenticate_kwargs['request'] = self.context['request']
    #     except KeyError:
    #         pass
    #
    #     # print(f"\nthis is the user of authenticate_kwargs {authenticate_kwargs['email']}\n")
    #
    #     '''
    #     Checking if the user exists by getting the email(username field) from authentication_kwargs.
    #     If the user exists we check if the user account is active.
    #     If the user account is not active we raise the exception and pass the message.
    #     Thus stopping the user from getting authenticated altogether.
    #
    #     And if the user does not exist at all we raise an exception with a different error message.
    #     Thus stopping the execution righ there.
    #     '''
    #     try:
    #         user = User.objects.get(username=authenticate_kwargs['username'])
    #         if not user.is_active:
    #             self.error_messages['no_active_account'] = _(
    #                 'The account is inactive'
    #             )
    #             raise exceptions.AuthenticationFailed(
    #                 self.error_messages['no_active_account'],
    #                 'no_active_account',
    #             )
    #     except User.DoesNotExist:
    #         self.error_messages['no_active_account'] = _(
    #             'Account does not exist')
    #         raise exceptions.AuthenticationFailed(
    #             self.error_messages['no_active_account'],
    #             'no_active_account',
    #         )
    #
    #     '''
    #     We come here if everything above goes well.
    #     Here we authenticate the user.
    #     The authenticate function return None if the credentials do not match
    #     or the user account is inactive. However here we can safely raise the exception
    #     that the credentials did not match as we do all the checks above this point.
    #     '''
    #
    #     self.user = authenticate(**authenticate_kwargs)
    #     if self.user is None:
    #         self.error_messages['no_active_account'] = _(
    #             'Credentials did not match')
    #         raise exceptions.AuthenticationFailed(
    #             self.error_messages['no_active_account'],
    #             'no_active_account',
    #         )
    #     return super().validate(attrs)

    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        data["client"] = None
        data["partner"] = None
        data["tours"] = []
        data["userId"] = self.user.id
        data["pick"] = self.user.pick
        if self.user.email_obj:
            data["email"] = EmailAddressSerializer(self.user.email_obj, many=False, allow_null=True).data
        if self.user.phone_obj:
            data["phone"] = PhoneNumberSerializer(self.user.phone_obj, many=False, allow_null=True).data

        related_user = self.user.related_user[0]
        if self.user.related_user[1] == "people":
            data["client"] = ProfileSerializer(related_user).data
        elif self.user.related_user[1] == "organization":
            data["partner"] = OrganizationSerializer(related_user).data
            data["tours"] = ToursOnOrganizationSerializer(related_user.tours.all(), many=True).data
        data['lifetime'] = int(refresh.access_token.lifetime.total_seconds())
        return data


class TokenRefreshLifetimeSerializer(TokenRefreshSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = RefreshToken(attrs['refresh'])
        data['lifetime'] = int(refresh.access_token.lifetime.total_seconds())
        return data


class ResponseRegisterSerializer(serializers.Serializer):
    access = serializers.CharField()


class RegisterUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=128, min_length=6, write_only=True)
    username = serializers.CharField(max_length=128, read_only=True)
    country = serializers.CharField(max_length=2, min_length=2, write_only=True, required=False)
    phone = PhoneNumberField(required=False)
    email = serializers.EmailField(required=False)
    first_name = serializers.CharField()
    last_name = serializers.CharField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'password', 'phone', 'country',
                  "first_name", "last_name")


class RegisterOrgSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=128, min_length=6, write_only=True)
    username = serializers.CharField(max_length=128, read_only=True)
    country = serializers.CharField(max_length=2, min_length=2, write_only=True)
    phone = PhoneNumberField(required=False)
    email = serializers.EmailField(required=False)
    org_type = serializers.ChoiceField(choices=OrgTypeChoice.choices)
    org_name = serializers.CharField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'password', 'phone', 'is_organization', "country", "pick",
                  "org_name", "org_type")


class CodeSerializer(serializers.Serializer):
    """ АПИ для кода """
    userId = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    hashCode = serializers.CharField()


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    phone = PhoneNumberField(required=False)


class PayHistoryHistorySerializer(serializers.ModelSerializer):
    number_type = serializers.StringRelatedField(source="cart.number.title")
    services_count = serializers.IntegerField(source="cart.get_services_count")
    status_name = serializers.StringRelatedField(source="get_status_display")
    tour_name = serializers.StringRelatedField(source="cart.tour.title")

    # TODO: need to optimizations here
    class Meta:
        model = Payment
        exclude = ("cart", "user", "status", "amount")


class PayHistoryHistoryDetailSerializer(serializers.ModelSerializer):
    number_type = serializers.StringRelatedField(source="cart.number.title")
    services_count = serializers.IntegerField(source="cart.get_services_count")
    status_name = serializers.StringRelatedField(source="get_status_display")
    file_field = serializers.FileField(allow_null=True)
    tour_name = serializers.StringRelatedField(source="cart.tour.title")
    reservations_start = serializers.DateField(source="reservation.reservation_date.lower", read_only=True)
    reservations_end = serializers.DateField(source="reservation.reservation_date.upper", read_only=True)

    # TODO: need to optimizations here
    class Meta:
        model = Payment
        exclude = ("cart", "user", "status", "created_at")


class UserVerifySerializer(serializers.Serializer):
    message = serializers.CharField()
    token = serializers.CharField(allow_null=True)


class PasswordResetChangeSerializer(serializers.Serializer):
    new_password1 = serializers.CharField(max_length=128)
    new_password2 = serializers.CharField(max_length=128)

    set_password_form_class = SetPasswordForm

    set_password_form = None

    def __init__(self, *args, **kwargs):
        self.old_password_field_enabled = False
        self.logout_on_password_change = False
        super().__init__(*args, **kwargs)

        self.request = self.context.get('request')
        self.user = getattr(self.request, 'user', None)

    def validate_old_password(self, value):
        invalid_password_conditions = (
            self.old_password_field_enabled,
            self.user,
            not self.user.check_password(value),
        )

        if all(invalid_password_conditions):
            err_msg = _('Your old password was entered incorrectly. Please enter it again.')
            raise serializers.ValidationError(err_msg)
        return value

    def custom_validation(self, attrs):
        pass

    def validate(self, attrs):
        self.set_password_form = self.set_password_form_class(
            user=self.user, data=attrs,
        )

        self.custom_validation(attrs)
        if not self.set_password_form.is_valid():
            raise serializers.ValidationError(self.set_password_form.errors)
        return attrs

    def save(self):
        self.set_password_form.save()
        if not self.logout_on_password_change:
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(self.request, self.user)


class PartUserCreateSerializer(serializers.Serializer):
    phone = PhoneNumberField()
    country = serializers.CharField(max_length=2, required=False, default="kz")
    first_name = serializers.CharField()
    last_name = serializers.CharField()


class ActivateCodeSerializer(serializers.Serializer):
    number = serializers.CharField(max_length=6)

    class Meta:
        model = ActivateCode
        fields = "__all__"


class Oauth2CodeSerializer(serializers.Serializer):
    code = serializers.CharField()
