from django.contrib import admin

from medtour.tourpackages.models import TourPackages, TourPackagesServices


class TourPackagesServicesInline(admin.TabularInline):
    model = TourPackagesServices
    extra = 1


@admin.register(TourPackages)
class TourPackagesAdmin(admin.ModelAdmin):
    list_select_related = ["tour__org"]
    raw_id_fields = ["tour", "number"]
    inlines = [TourPackagesServicesInline]


@admin.register(TourPackagesServices)
class TourPackagesServicesAdmin(admin.ModelAdmin):
    raw_id_fields = ["package"]
    list_display = ["package", "title", "hide"]
    list_filter = ["package", "package__tour"]
    search_fields = ["package__title", "package__tour__title"]
