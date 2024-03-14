from django.contrib import admin

from .models import Reservations, ReservationsServices, ReservationsPackage


@admin.register(Reservations)
class ReservationsAdmin(admin.ModelAdmin):
    list_select_related = [
        "number_cabinets",
        "reservator",
        "partner",
        "tour",
        "number__tour__org",
    ]
    raw_id_fields = [
        "number_cabinets",
        "number",
        "reservator",
        "partner",
        "tour"
    ]
    list_editable = ["is_deleted"]
    list_display = ["get_tour", "is_deleted",
                    # "number__title"
                    "get_number_title",
                    "paid",
                    "reservation_date",
                    "fullName",
                    "reservator",
                    "number_cabinets_id",
                    "payment",
                    ]

    @admin.display(ordering="number__tour__title", description="Номера")
    def get_number_title(self, obj):
        return obj.number.title

    @admin.display(ordering="tour__title", description="Туры")
    def get_tour(self, obj):
        return obj.tour.title


@admin.register(ReservationsServices)
class ReservationsServicesAdmin(admin.ModelAdmin):
    pass


@admin.register(ReservationsPackage)
class ReservationsPackageAdmin(admin.ModelAdmin):
    pass
