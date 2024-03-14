from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from phone_auth.models import EmailAddress, PhoneNumber

from medtour.users.forms import UserAdminChangeForm, UserAdminCreationForm
from medtour.users.models import Person, Organization, OrganizationCategory, Country, Region, ActivateCode, \
    RestoreCode, City

User = get_user_model()


class EmailAddressInline(admin.TabularInline):
    model = EmailAddress
    extra = 0


class PhoneNumberInline(admin.TabularInline):
    model = PhoneNumber
    extra = 0


class CustomUserAdmin(auth_admin.UserAdmin):
    ordering = ("username",)
    list_display = ('username', 'first_name', 'last_name', 'is_staff')
    search_fields = ('first_name', 'last_name',)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )


@admin.register(User)
class UserAdmin(CustomUserAdmin):
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm
    fieldsets = (
        (None, {"fields": ("username", "password", "avatar")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                    "is_organization",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    list_display = ["id", "username", "is_superuser", "is_organization", "get_type_user"]
    list_select_related = ["people"]
    list_display_links = ['username', 'is_superuser']
    inlines = [EmailAddressInline, PhoneNumberInline]

    @admin.display(description=_("Наименование"), empty_value=_("Не указан имя"))
    def get_type_user(self, obj):
        return obj.organization.org_name if hasattr(obj, "organization") else obj.people.first_name


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    raw_id_fields = ["user", "region", "country"]


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    raw_id_fields = ["user"]


@admin.register(OrganizationCategory)
class OrganizationCategoryAdmin(admin.ModelAdmin):
    list_display = ["title"]


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ['name']
    raw_id_fields = ["country"]


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_first_page']
    raw_id_fields = ["region"]
    list_editable = ["is_first_page"]


class CodeAdmin(admin.ModelAdmin):
    raw_id_fields = ["user"]
    list_display = ['user', 'number', 'created_at']


admin.site.register(ActivateCode, CodeAdmin)
admin.site.register(RestoreCode, CodeAdmin)
