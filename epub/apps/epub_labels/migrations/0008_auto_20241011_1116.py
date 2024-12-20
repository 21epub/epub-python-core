# Generated by Django 3.2.22 on 2024-10-11 03:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('epub_labels', '0007_auto_20230301_1352'),
    ]

    operations = [
        migrations.AddField(
            model_name='label',
            name='expression',
            field=models.TextField(blank=True, help_text='计算项表达式', null=True),
        ),
        migrations.AlterField(
            model_name='label',
            name='input_type',
            field=models.IntegerField(choices=[(0, 'single'), (1, 'multiple'), (2, 'input'), (3, 'bool'), (5, 'expression')]),
        ),
    ]
