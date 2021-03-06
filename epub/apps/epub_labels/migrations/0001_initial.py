# Generated by Django 3.1 on 2021-04-01 13:04

import epub.apps.epub_labels.models.db
from django.db import migrations, models
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Label",
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
                (
                    "created",
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="created",
                    ),
                ),
                (
                    "modified",
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="modified",
                    ),
                ),
                (
                    "status",
                    models.IntegerField(choices=[(0, "草稿"), (1, "已发布")], default=0),
                ),
                (
                    "status_changed",
                    model_utils.fields.MonitorField(
                        default=django.utils.timezone.now,
                        monitor="status",
                        verbose_name="status changed",
                    ),
                ),
                ("is_removed", models.BooleanField(default=False)),
                ("user_id", models.IntegerField(default=None, null=True)),
                ("subuser_id", models.IntegerField(default=None, null=True)),
                ("nickname", models.CharField(default="", max_length=150, null=True)),
                ("cid", models.CharField(max_length=63)),
                (
                    "serial_number",
                    models.BigIntegerField(
                        default=epub.apps.epub_labels.models.db.gen_serial_number,
                        editable=False,
                    ),
                ),
                ("title", models.CharField(max_length=63)),
                (
                    "description",
                    models.CharField(blank=True, default="", max_length=511, null=True),
                ),
                (
                    "value_type",
                    models.IntegerField(
                        choices=[(0, "text"), (1, "number"), (2, "list")]
                    ),
                ),
                (
                    "input_type",
                    models.IntegerField(
                        choices=[(0, "single"), (1, "multiple"), (2, "input")]
                    ),
                ),
                ("maximum_depth", models.IntegerField(default=1)),
                ("enabled", models.BooleanField(default=True)),
                ("allow_check_parent", models.BooleanField(default=False, null=True)),
                ("allow_add_items", models.BooleanField(default=False, null=True)),
                ("items", models.JSONField(blank=True, null=True)),
            ],
            options={
                "ordering": ["created"],
            },
        ),
    ]
