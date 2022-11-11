from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Workspaces, Payroll_time_period, TimeType, Work_time_period, Work, Gps, Crew
from django.contrib.postgres.fields import ArrayField

"""
User Serializer
"""
class UserSerializer(serializers.ModelSerializer):
    password = serializers.HiddenField(default = "")
    class Meta:
        model = User
        fields= ("id", "first_name", "last_name", "email", "username", "password", "last_login", "is_superuser")


"""
TimeType Serializer    
"""
class TimeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeType
        fields = ("id", "name", "type", "pay_type", "workspace_id")

"""
Workspace Serializer
"""
class WorkspacesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workspaces
        fields = ("id", "name")

"""
Payroll Time Period Serializer
"""
class PayrollTimePeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payroll_time_period
        fields = ("id","workspace_id", "user_id", "start_time", "stop_time", "start_gps", "stop_gps", "approved", "note")


"""
Payroll Report Serializer
"""
class PayrollReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payroll_time_period
        fields = ("id","workspace_id", "user_id", "start_time", "stop_time", "start_gps", "stop_gps", "approved", "note")



"""
Work Serializer
"""
class WorkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Work
        fields = ("id", "user_id", "name", "payroll_time_period_id", "workspace_id")


"""
Gps Serializer
"""
class GpsSerializer(serializers.ModelSerializer):
    # gps_point = serializers.ListField(child=serializers.FloatField(), allow_empty=False)
    class Meta:
        model = Gps
        fields = ("id", "user_id", "work_time_period_id", "workspace_id", "gps_point", "timestamp")

"""
Crew Serializer
"""
class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "name", "active", "workspace_id", "foreman_user_id", "crew_users")

"""
Work Time Period Serializer
"""
class WorkTimePeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Work_time_period
        fields = ("id", "workspace_id", "user_id", "work_id", "timetype_id", "start_time", "stop_time", "start_gps", "stop_gps", "mileage", "approved", "note")


"""
Payroll Report Serializer
"""
class PayrollReportSerializer(serializers.ModelSerializer):
    duration = serializers.IntegerField()

    class Meta:
        model = Work_time_period
        fields = ("id", "workspace_id", "user_id", "work_id", "timetype_id", "start_time", "stop_time", "start_gps", "stop_gps", "mileage", "approved", "note",
        "duration" # additional fields
        )


"""
Time sheet Serializer
"""
class TimeSheetSerializer(serializers.ModelSerializer):
    duration = serializers.IntegerField()

    class Meta:
        model = Payroll_time_period
        fields = (
            "start_time", "stop_time", "note",
            "duration" # additional fields
        )

class TimeUtilizationPayrollSerializer(serializers.ModelSerializer):
    payroll_time = serializers.IntegerField()
    
    class Meta:
        model = Payroll_time_period
        fields = (
            "payroll_time", "user_id", "start_time", "stop_time"
        )

class TimeUtilizationWorkTimeSerializer(serializers.ModelSerializer):
    duration = serializers.IntegerField()
    
    class Meta:
        model = Work_time_period
        fields = (
            "name", "duration"
        )


"""
Payroll Report Serializer
"""
class WorkReportSerializer(serializers.ModelSerializer):
    duration = serializers.IntegerField()
    # @dev unknown field 'full_name'

    class Meta:
        model = Work_time_period
        fields = ("user", "id", "workspace_id", "user_id", "work_id", "timetype_id", "start_time", "stop_time", "start_gps", "stop_gps", "mileage", "approved", "note",
        "duration" # additional fields
        )

"""
Active Time Serializer for Work_time_period
"""
class ActiveTimeWorkTimeSerializer(serializers.ModelSerializer):
    time_type = serializers.CharField(source='timetype.name')
    gps_point = serializers.ListField(child=serializers.FloatField(), source='start_gps')
    #time_log_time = ''

    class Meta:
        model = Work_time_period
        fields = ("id", "gps_point", "timetype_id", "work_id", "time_type")


"""
Active Time Serializer for Payroll
"""
class ActiveTimeWorkPayrollSerializer(serializers.ModelSerializer):
    time_type = serializers.CharField(source='timetype.name')
    gps_point = serializers.ListField(child=serializers.FloatField(), source='start_gps')

    class Meta:
        model = Payroll_time_period
        fields = ("id", "gps_point", "timetype_id", "work_id", "time_type")
