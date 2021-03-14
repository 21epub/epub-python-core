# Generated by Django 3.1 on 2021-01-28 03:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('epub_auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(db_index=True, help_text='Required. 30 characters or fewer. Letters, numbers and @/./+/-/_ characters', max_length=30, verbose_name='用户名')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='名字')),
                ('last_name', models.CharField(blank=True, max_length=30, verbose_name='姓氏')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='e-mail address')),
                ('password', models.CharField(max_length=128, verbose_name='密码')),
                ('is_active', models.BooleanField(default=True, help_text='指明用户是否被认为是活跃的。以反选代替删除帐号。', verbose_name='有效')),
                ('can_publish', models.BooleanField(default=False)),
                ('can_pack', models.BooleanField(default=False)),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, verbose_name='上次登录')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='加入日期')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subusers', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]