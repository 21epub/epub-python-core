# Generated by Django 3.1 on 2021-07-19 02:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Folder",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                ("position", models.PositiveIntegerField(default=65536)),
                ("user_id", models.IntegerField(db_index=True, null=True)),
                ("subuser_id", models.IntegerField(db_index=True, null=True)),
                ("folder_type", models.CharField(max_length=32)),
                ("lft", models.PositiveIntegerField(editable=False)),
                ("rght", models.PositiveIntegerField(editable=False)),
                ("tree_id", models.PositiveIntegerField(db_index=True, editable=False)),
                ("level", models.PositiveIntegerField(editable=False)),
                (
                    "parent",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="children",
                        to="epub_folders.folder",
                        verbose_name="parent",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
