from django.urls import path

from medtour.paycredentials.views import Kassa24CallbackView

app_name = "medtour.paycredentials"

urlpatterns = [
    path('kassa24/', Kassa24CallbackView.as_view(), name='kassa24'),
]
