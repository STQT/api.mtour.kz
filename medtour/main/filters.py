import django_filters

from medtour.users.models import City


class CityFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = City
        fields = ['name']
