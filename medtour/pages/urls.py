from django.urls import path

from medtour.pages.views import (
    get_docs
)


app_name = "medtour.pages"
urlpatterns = [
    # HTML endpoints
    path("public_offer_of_legal_entities.html", get_docs, name="public_offer"),
    path("public_offer_of_individuals.html", get_docs, name="public_offer_for_individual"),
    path("USER_PERSONAL_DATA_PROTECTION_AGREEMENT.html", get_docs, name="protection_agreement"),
    path("user_rules.html", get_docs, name="user_rules"),  # "user_rules.html SiteRules
    path("order_rules.html", get_docs, name="order_rules"),  # "order_rules"
    path("refunds.html", get_docs, name="refunds"),
]
