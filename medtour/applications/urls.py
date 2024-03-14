from django.urls import path

from medtour.applications.views import (
    ApplicationCreateView
)


app_name = "medtour.applications"

urlpatterns = [
    path("", ApplicationCreateView.as_view(), name="create"),
]
