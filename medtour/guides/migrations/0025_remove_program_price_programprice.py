# Generated by Django 4.1.9 on 2023-07-01 08:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("guides", "0024_program_programservices_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="program",
            name="price",
        ),
        migrations.CreateModel(
            name="ProgramPrice",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "price_type",
                    models.CharField(
                        choices=[
                            (0, "Для всех"),
                            (1, "Для детей"),
                            (2, "Для студентов"),
                            (3, "Для пенсионеров"),
                            (4, "Для других"),
                        ],
                        default=0,
                        max_length=10,
                    ),
                ),
                ("is_main", models.BooleanField(default=False)),
                ("cost", models.IntegerField()),
                (
                    "program",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="program_prices", to="guides.program"
                    ),
                ),
            ],
        ),
    ]
