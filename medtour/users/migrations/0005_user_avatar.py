# Generated by Django 3.2.15 on 2023-03-26 20:14

from django.db import migrations
import sorl.thumbnail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_organization_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='avatar',
            field=sorl.thumbnail.fields.ImageField(blank=True, null=True, upload_to='avatars/%y/%m/%d', verbose_name='Аватар профиля'),
        ),
    ]