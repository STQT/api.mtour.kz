from django.contrib import admin

from medtour.guides.models import (Guide, GuideReview,
                                   GuideShots, GuideProgram, GuideServices, GuideCategory)


@admin.register(Guide)
class GuideAdmin(admin.ModelAdmin):
    list_display = ["title", "org"]


@admin.register(GuideReview)
class GuideReviewAdmin(admin.ModelAdmin):
    pass


@admin.register(GuideShots)
class GuideShotsAdmin(admin.ModelAdmin):
    pass


@admin.register(GuideProgram)
class GuideProgramAdmin(admin.ModelAdmin):
    raw_id_fields = ['guide']
    list_select_related = ['guide']


@admin.register(GuideServices)
class GuideServicesAdmin(admin.ModelAdmin):
    pass


@admin.register(GuideCategory)
class GuideCategoryAdmin(admin.ModelAdmin):
    pass
