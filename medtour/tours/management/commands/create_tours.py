from django.core.management.base import BaseCommand
from faker import Faker

from medtour.tours.models import Tour
from medtour.users.models import Country, Region, OrganizationCategory

x = Faker.seed(0)
fake = Faker('ru-RU')
print(fake.bs(), type(fake.bs()), len(fake.bs()))


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        for i in range(300):
            for country in Country.objects.all():
                regions = Region.objects.filter(country=country)
                for region in regions:
                    categories = OrganizationCategory.objects.all()
                    for category in categories:
                        t = Tour.objects.create(
                            title="Тур: {} |".format(
                                fake.bs(),
                            ),
                            region=region,
                            country=country,
                            category=category
                        )
                        self.stdout.write(self.style.SUCCESS('Successfully closed poll "%s"' % t))
