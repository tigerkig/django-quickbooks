from django.urls import path
from . import views

urlpatterns = [
    path("payroll_time_period", views.PayrollTimePeriodView.as_view(), name="payroll_time_period"),
    path("timetype", views.TimeTypeView.as_view(), name="timetype"),
    path("work_time_period", views.WorkTimePeriodView.as_view(), name="work_time_period"),
    path("gps", views.GpsView.as_view(), name="gps"),
    path("gps_path", views.GpsPathView.as_view(), name="time_sheet"),
    path("current_gps", views.CurrentGpsView.as_view(), name="current_gps"),
    path("workspace", views.WorkspacesView.as_view(), name="workspace"),
    path("crew", views.CrewView.as_view(), name="crew"),
    path("user", views.UserView.as_view(), name="user"),
    path("payroll_report", views.PayrollReportView.as_view(), name="payroll_report"),
    path("work", views.WorkView.as_view(), name="work"),
    path("time_sheet", views.TimeSheetView.as_view(), name="time_sheet"),
    path("time_utilization", views.TimeUtilizationView.as_view(), name="time_utilization"),
    path("work_report", views.WorkReportView.as_view(), name="work_report"),
    path("active_time", views.ActiveTimeView.as_view(), name="active_time"),
]