# Generated by Django 3.2.12 on 2022-05-08 15:25

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('username', models.CharField(default='', max_length=30, unique=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('session_key', models.CharField(blank=True, default='', max_length=200, null=True)),
                ('recovery_code', models.PositiveIntegerField(default=0)),
                ('verified_by_code', models.BooleanField(default=False)),
                ('is_staff', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
