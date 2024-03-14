from django.urls import path

from medtour.main.views import NumbersProgramsView, CitySearchAPIView, CategoriesListAPIView

app_name = "medtour.main"

urlpatterns = [
    path("records/<str:city>/<str:entity>/", NumbersProgramsView.as_view(), name="tour_guides"),
    path('address/cities/search/', CitySearchAPIView.as_view(), name='city_search'),
    path('categories/', CategoriesListAPIView.as_view(), name='categories_list'),
]
