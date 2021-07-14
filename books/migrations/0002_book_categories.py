# Generated by Django 3.1 on 2021-07-13 07:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('epub_categories', '0001_initial'),
        ('books', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='categories',
            field=models.ManyToManyField(default=django.db.models.deletion.CASCADE, related_name='book_set', to='epub_categories.Category'),
        ),
    ]
