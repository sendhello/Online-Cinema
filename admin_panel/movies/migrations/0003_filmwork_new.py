# Generated by Django 4.1.7 on 2023-07-18 18:57

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("movies", "0002_add_indexes"),
    ]

    operations = [
        migrations.AddField(
            model_name="filmwork",
            name="new",
            field=models.BooleanField(
                blank=True, default=False, null=True, verbose_name="new"
            ),
        ),
    ]