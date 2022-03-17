# Generated by Django 3.1.12 on 2022-03-17 03:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("epub_folders", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="folder",
            options={"ordering": ["position"]},
        ),
        migrations.RemoveField(
            model_name="folder",
            name="level",
        ),
        migrations.RemoveField(
            model_name="folder",
            name="lft",
        ),
        migrations.RemoveField(
            model_name="folder",
            name="rght",
        ),
        migrations.RemoveField(
            model_name="folder",
            name="tree_id",
        ),
        migrations.AlterField(
            model_name="folder",
            name="parent",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="children",
                to="epub_folders.folder",
                verbose_name="parent",
            ),
        ),
    ]
