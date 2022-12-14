# Generated by Django 4.0.3 on 2022-11-03 08:48

import django.contrib.postgres.fields
from django.db import migrations, models
import django_postgres_timestamp_without_tz


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Crew',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('active', models.BooleanField(default=False)),
                ('workspace_id', models.IntegerField()),
                ('foreman_user_id', models.IntegerField()),
                ('crew_user_ids', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), blank=True, size=None)),
            ],
            options={
                'db_table': 'crew',
            },
        ),
        migrations.CreateModel(
            name='Gps',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('user_id', models.IntegerField()),
                ('workspace_id', models.IntegerField(null=True)),
                ('gps_point', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(), blank=True, size=None)),
                ('timestamp', django_postgres_timestamp_without_tz.DateTimeWithoutTZField(blank=True, default='2022-11-03 04:48:35')),
            ],
            options={
                'db_table': 'gps',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Payroll_time_period',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('workspace_id', models.IntegerField()),
                ('user_id', models.IntegerField()),
                ('start_time', django_postgres_timestamp_without_tz.DateTimeWithoutTZField(default='2022-11-03 04:48:35', null=True)),
                ('stop_time', django_postgres_timestamp_without_tz.DateTimeWithoutTZField(blank=True, null=True)),
                ('start_gps', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(), null=True, size=None)),
                ('stop_gps', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(), null=True, size=None)),
                ('approved', models.BooleanField(default=False)),
                ('note', models.TextField(null=True)),
            ],
            options={
                'db_table': 'payroll_time_period',
            },
        ),
        migrations.CreateModel(
            name='TimeType',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('workspace_id', models.IntegerField()),
                ('type', models.CharField(max_length=255)),
                ('pay_type', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'timetype',
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('full_name', models.CharField(max_length=255)),
                ('email', models.CharField(max_length=255, unique=True)),
                ('username', models.CharField(max_length=255, unique=True)),
                ('password', models.CharField(max_length=255)),
                ('admin', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'users',
            },
        ),
        migrations.CreateModel(
            name='Work',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('payroll_time_period_id', models.IntegerField()),
                ('workspace_id', models.IntegerField()),
                ('user_id', models.IntegerField()),
            ],
            options={
                'db_table': 'work',
            },
        ),
        migrations.CreateModel(
            name='Work_time_period',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('workspace_id', models.IntegerField(null=True)),
                ('user_id', models.IntegerField(null=True)),
                ('work_id', models.IntegerField(null=True)),
                ('timetype_id', models.IntegerField(null=True)),
                ('start_time', django_postgres_timestamp_without_tz.DateTimeWithoutTZField(blank=True, default='2022-11-03 04:48:35')),
                ('stop_time', django_postgres_timestamp_without_tz.DateTimeWithoutTZField(blank=True, null=True)),
                ('start_gps', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(), blank=True, null=True, size=None)),
                ('stop_gps', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(), blank=True, null=True, size=None)),
                ('mileage', models.CharField(max_length=255, null=True)),
                ('approved', models.BooleanField(default=False)),
                ('note', models.TextField(null=True)),
            ],
            options={
                'db_table': 'work_time_period',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Workspaces',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('timetypd_id', models.IntegerField()),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'workspaces',
            },
        ),
    ]
