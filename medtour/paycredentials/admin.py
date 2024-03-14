from django.contrib import admin

from medtour.paycredentials.models import Kassa24Credentials


@admin.register(Kassa24Credentials)
class Kassa24CredentialsAdmin(admin.ModelAdmin):
    pass
