from django.contrib import admin
from django.http import HttpResponseForbidden
from django.utils.translation import gettext_lazy as _

from .models import (PublicOffer, OrderRules, PersonalInfoProtection, Refunds,
                     SiteRules, PublicOfferForIndividual)


class EditingProtectModelAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        if obj and obj.should_be_read_only:
            return 'title', 'content'
        else:
            return ()

    def change_view(self, request, object_id, form_url='', extra_context=None):
        obj = self.get_object(request, object_id)
        if obj and obj.title:
            return HttpResponseForbidden(_("Нельзя редактировать документы"))
        else:
            return super().change_view(request, object_id, form_url=form_url, extra_context=extra_context)


admin.site.register(PublicOffer, EditingProtectModelAdmin)
admin.site.register(SiteRules, EditingProtectModelAdmin)
admin.site.register(Refunds, EditingProtectModelAdmin)
admin.site.register(PersonalInfoProtection, EditingProtectModelAdmin)
admin.site.register(OrderRules, EditingProtectModelAdmin)
admin.site.register(PublicOfferForIndividual, EditingProtectModelAdmin)
