from django.contrib import admin

from medtour.subscriptions.models import SubscribePrice, TourSubscribe


@admin.register(SubscribePrice)
class SubscribePriceAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'created_at', 'numbers_of_months', 'is_actual']

    # protect editing exist objects
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return 'price',
        return []


@admin.register(TourSubscribe)
class TourSubscribeAdmin(admin.ModelAdmin):
    pass
