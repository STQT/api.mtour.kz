from django.contrib import admin

from medtour.orders.models import ServiceCartPackages, ServiceCartServices, ServiceCart, Payment, ServiceCartVisitors


class ServiceCartPackagesInline(admin.TabularInline):
    model = ServiceCartPackages
    extra = 1


class ServiceCartServicesInline(admin.TabularInline):
    model = ServiceCartServices
    extra = 1


@admin.register(ServiceCart)
class ServiceCartAdmin(admin.ModelAdmin):
    raw_id_fields = ["tour", "user", "number"]
    inlines = [ServiceCartPackagesInline, ServiceCartServicesInline]


@admin.register(ServiceCartServices)
class ServiceCartServicesAdmin(admin.ModelAdmin):
    raw_id_fields = ["service", "service_cart"]


@admin.register(ServiceCartPackages)
class ServiceCartPackagesAdmin(admin.ModelAdmin):
    raw_id_fields = ["package", "service_cart"]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    raw_id_fields = ["user", "cart"]
    list_display = ["user", "status", "amount", "cart", "tour_display", "is_partial", "created_at"]
    list_display_links = ["user", "cart"]

    def tour_display(self, obj):
        return obj.cart.tour

    tour_display.allow_tags = True
    tour_display.short_description = 'Тур'


@admin.register(ServiceCartVisitors)
class ServiceCartVisitorsAdmin(admin.ModelAdmin):
    list_fields = ["first_name", "last_name"]
