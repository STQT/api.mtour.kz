# Generated by Django 3.2.15 on 2023-03-29 16:46

from django.db import migrations
import medtour.guides.instances
import sorl.thumbnail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('guides', '0007_alter_guideprogram_photo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='guideprogram',
            name='photo',
            field=sorl.thumbnail.fields.ImageField(blank=True, null=True, upload_to=medtour.guides.instances.get_program_path, verbose_name='Изображение программы'),
        ),
    ]
