from pyexpat import model
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.postgres.fields import ArrayField
from datetime import datetime
from django.db import connection
# from wherever.fields import DateTimeWithoutTZField as DateTimeField
from django_postgres_timestamp_without_tz import DateTimeWithoutTZField
from .managers import CustomUserManager

User=get_user_model()

"""
Custom User Model
"""
"""
#class CustomUser(AbstractBaseUser, PermissionsMixin):
class User(models.Model):
    id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, max_length=255)
    username = models.CharField(unique=True, max_length=255)
    password = models.CharField(max_length=255)
    admin = models.BooleanField(default=False)
    
    class Meta:
	    db_table = "users"
"""

"""
workspaces model
"""
class Workspaces(models.Model):
     id = models.AutoField(primary_key=True)
     name = models.CharField(max_length=255)

     class Meta:
	     db_table = "workspaces"

"""
timetype model
"""
class TimeType(models.Model):
     id = models.AutoField(primary_key=True)
     name = models.CharField(max_length=255)
     workspace = models.ForeignKey(Workspaces, on_delete=models.CASCADE, related_name="timetype")
     type = models.CharField(max_length=255)
     pay_type = models.CharField(max_length=255)
     class Meta:
	     db_table = "timetype"


"""
crew model
"""
class Crew(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    active = models.BooleanField(default=False)
    workspace = models.ForeignKey(Workspaces, on_delete=models.CASCADE, null=True)
    foreman_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    crew_users = models.ManyToManyField(User, related_name="crew_users", blank=True)
    class Meta:
	    db_table = "crew"

"""
payroll_time_period model
"""
class Payroll_time_period(models.Model):
    id = models.AutoField(primary_key=True)
    workspace = models.ForeignKey(Workspaces, on_delete=models.CASCADE, related_name="payroll_time_period", null=True)
    # this should be from associate with User table
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payroll_time_period", null=True)
    start_time = DateTimeWithoutTZField(default=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), null=True) 
    stop_time = DateTimeWithoutTZField(null=True, blank=True)
    start_gps = ArrayField(models.FloatField(), null=True)
    stop_gps = ArrayField(models.FloatField(), null=True)
    approved = models.BooleanField(default=False)
    note = models.TextField(null=True)

    class Meta:
        db_table = "payroll_time_period"


class Gps(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="gps", null=True)
    work_time_period = models.ForeignKey('Work_time_period', on_delete=models.CASCADE, null=True)
    workspace = models.ForeignKey(Workspaces, on_delete=models.CASCADE, null=True)
    gps_point = ArrayField(models.FloatField(), blank=True)
    timestamp = DateTimeWithoutTZField(default=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), blank=True)
    class Meta:
        managed = True
        db_table = "gps"


class Work(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="work", null=True)
    name = models.CharField(max_length=255)
    payroll_time_period = models.ForeignKey(Payroll_time_period, on_delete=models.CASCADE, null=True, blank=True, related_name="work")
    workspace = models.ForeignKey(Workspaces, on_delete=models.CASCADE, related_name="work", null=True)

    class Meta:
	    db_table = "work"


class Work_time_period(models.Model):
    id = models.AutoField(primary_key=True)
    workspace = models.ForeignKey(Workspaces, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    work = models.ForeignKey(Work, on_delete=models.CASCADE, null=True)
    timetype = models.ForeignKey(TimeType, on_delete=models.CASCADE, null=True)
    start_time = DateTimeWithoutTZField(default=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), blank=True)
    stop_time = DateTimeWithoutTZField(null=True, blank=True)
    start_gps = ArrayField(models.FloatField(), null=True, blank=True)
    stop_gps = ArrayField(models.FloatField(), null=True, blank=True)
    mileage = models.CharField(max_length=255, null=True)
    approved = models.BooleanField(default=False)
    note = models.TextField(null=True)
   
    class Meta:
        managed = True
        db_table = "work_time_period"