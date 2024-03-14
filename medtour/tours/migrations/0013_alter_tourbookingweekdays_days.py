# Generated by Django 3.2.15 on 2023-04-06 11:29

from django.db import migrations
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('tours', '0012_remove_tour_working_hours'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tourbookingweekdays',
            name='days',
            field=multiselectfield.db.fields.MultiSelectField(choices=[(0, 'ПОНЕДЕЛЬНИК'), (1, 'ВТОРНИК'), (2, 'СРЕДА'), (3, 'ЧЕТВЕРГ'), (4, 'ПЯТНИЦА'), (5, 'СУББОТА'), (6, 'ВОСКРЕСЕНЬЕ')], default=[0, 1, 2, 3, 4, 5, 6], max_length=13),
        ),
    ]
