from django.shortcuts import render
from django.urls import resolve

from medtour.pages.models import (
    PublicOffer, PersonalInfoProtection, Refunds, SiteRules, OrderRules, PublicOfferForIndividual
)


def get_docs(request):
    content = {
        "public_offer": PublicOffer,  # yes
        "public_offer_for_individual": PublicOfferForIndividual,
        "protection_agreement": PersonalInfoProtection,
        "user_rules": SiteRules,  # SiteRules
        "order_rules": OrderRules,
        "refunds": Refunds,
    }
    current_url = resolve(request.path_info).url_name
    content_data = content[current_url].objects.order_by("-id").first()
    return render(request, "pages/docs.html", context={"data": content_data})
