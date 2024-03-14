from django.contrib import admin

from medtour.applications.models import Application, TourApplication


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    raw_id_fields = ["region", "category"]
    list_display = ["fullName", "created_at", "get_category"]

    @admin.display(ordering="category__title", description="Категория")
    def get_category(self, obj):
        return obj.category.title


@admin.register(TourApplication)
class TourApplicationAdmin(admin.ModelAdmin):
    list_display = ["get_fullname", "get_category", "get_phone", "tour", "status"]
    list_select_related = ["application__category", "tour"]

    @admin.display(ordering="application__fullName", description="Имя лида")
    def get_fullname(self, obj):
        return obj.application.fullName

    @admin.display(ordering="application__category__title", description="Категория")
    def get_category(self, obj):
        return obj.application.category.title

    @admin.display(ordering="application__phoneNumber", description="Телефон")
    def get_phone(self, obj):
        return obj.application.phoneNumber
