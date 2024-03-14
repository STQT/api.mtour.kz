from django.contrib import admin
from ordered_model.admin import OrderedModelAdmin

from medtour.tournumbers.models import (
    TourNumbers, TourNumbersServices, NumberCabinets, NumberComfort,
    NumberShots)


class TourNumbersServicesInline(admin.TabularInline):
    model = TourNumbersServices
    extra = 1


@admin.register(TourNumbers)
class TourNumbersAdmin(admin.ModelAdmin):
    inlines = [TourNumbersServicesInline]
    list_display = ["title", "remarks", "tour", "place_count", "price"]
    list_filter = (
        ('tour', admin.RelatedOnlyFieldListFilter),
    )
    search_fields = ("tour__title",)
    raw_id_fields = ["tour", "comforts"]


@admin.register(TourNumbersServices)
class TourNumbersServicesAdmin(admin.ModelAdmin):
    list_display = ["title", "tour_number", "hide"]
    raw_id_fields = ["tour_number"]
    list_filter = ["tour_number", "tour_number__tour"]
    search_fields = ["tour_number__title", "tour_number__tour__title"]


@admin.register(NumberCabinets)
class PackageCabinetsAdmin(admin.ModelAdmin):
    list_select_related = ["tour_number", "tour_number__tour"]
    list_filter = (
        ('tour_number', admin.RelatedOnlyFieldListFilter),
    )
    search_fields = ("tour_number__title",)
    list_display = ("tour_number", "number", "humanize_name", "tour_display")
    raw_id_fields = ["tour_number"]

    def tour_display(self, obj):
        return obj.tour_number.tour

    tour_display.allow_tags = True
    tour_display.short_description = 'Тур'


@admin.register(NumberComfort)
class NumberComfortAdmin(admin.ModelAdmin):
    pass


@admin.register(NumberShots)
class NumberShotsAdmin(OrderedModelAdmin):
    raw_id_fields = ["tour_number"]
    list_display = ["id", "name", "move_up_down_links", "tour_number", "order"]
    ordering = ["tour_number", "order"]
