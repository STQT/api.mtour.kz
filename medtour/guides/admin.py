from django.contrib import admin

from medtour.guides.models import (
    Program, ProgramServices, GuideCategory, ProgramInfoSchedule,
    ProgramPlaces, ProgramShots, ProgramReview)


class ProgramInfoScheduleInline(admin.TabularInline):
    model = ProgramInfoSchedule
    extra = 0


class ProgramPlacesInline(admin.TabularInline):
    model = ProgramPlaces
    extra = 0


class ProgramInline(admin.TabularInline):
    model = Program
    extra = 0


class ProgramShotsInline(admin.TabularInline):
    model = ProgramShots
    extra = 0


@admin.register(ProgramReview)
class ProgramReviewAdmin(admin.ModelAdmin):
    pass


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    raw_id_fields = ['tour']
    list_select_related = ['tour']
    inlines = [
        ProgramShotsInline,
        ProgramInfoScheduleInline,
        ProgramPlacesInline,
    ]


@admin.register(ProgramServices)
class ProgramServicesAdmin(admin.ModelAdmin):
    pass


@admin.register(GuideCategory)
class GuideCategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(ProgramInfoSchedule)
class ProgramScheduleAdmin(admin.ModelAdmin):
    pass


@admin.register(ProgramPlaces)
class ProgramPlacesAdmin(admin.ModelAdmin):
    pass


@admin.register(ProgramShots)
class ProgramShotsAdmin(admin.ModelAdmin):
    pass
