# Generated by Django 3.1.6 on 2021-04-08 04:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("epub_labels", "0002_applabel"),
    ]

    operations = [
        migrations.AlterField(
            model_name="label",
            name="value_type",
            field=models.IntegerField(choices=[(0, "text"), (1, "number")]),
        ),
    ]
