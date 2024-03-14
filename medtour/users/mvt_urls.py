from django.urls import path

from medtour.users.views import (
    user_detail_view,
    user_redirect_view,
    user_update_view,
)
from medtour.utils.views import GeneratePDF

app_name = "mvt_users"
urlpatterns = [
    # HTML endpoints
    path("~redirect/", view=user_redirect_view, name="redirect"),
    path("~update/", view=user_update_view, name="update"),
    path("pdf/", GeneratePDF.as_view(), name="pdf"),
    path("<str:username>/", view=user_detail_view, name="detail"),
]
