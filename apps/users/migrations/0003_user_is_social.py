# Generated by Django 4.2.14 on 2024-08-04 15:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_resetpassword'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_social',
            field=models.BooleanField(default=False),
        ),
    ]
