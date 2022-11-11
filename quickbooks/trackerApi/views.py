from django.shortcuts import render
from psycopg2 import Timestamp
from rest_framework.decorators import api_view
from django.http import JsonResponse
from django.db import connection
from django.db.models import Q, F, Sum
from django.db.models.functions import  Round, Cast
import haversine as hs        # calculate distance between two gps points
from haversine import Unit    # distance unit
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime

from rest_framework import status
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from .functions import Epoch

from .models import Payroll_time_period, TimeType, Workspaces, Work_time_period, Work, Gps, Crew, User
from . import serializers

#from .serializers import TimeTypeSerializer, WorkspacesSerializer, GpsSerializer, PayrollTimePeriodSerializer, CrewSerializer, UserSerializer, WorkTimePeriodSerializer, PayrollReportSerializer, WorkSerializer, TimeSheetSerializer, TimeUtilizationPayrollSerializer

"""
Workspaces view class
"""
class WorkspacesView(APIView):
    # GET
    def get(self, request):
        queryset = Workspaces.objects.all()

        workspaces_serializer = serializers.WorkspacesSerializer(queryset, many=True)

        return JsonResponse(workspaces_serializer.data, safe=False)

    # POST
    def post(self, request):
        serializer = serializers.WorkspacesSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return JsonResponse("success", safe=False)
        
        return JsonResponse(serializer.errors, safe=False)
    
    # PATCH
    def patch(self, request):
        id = request.data.get("id", None)

        try:
            workspace = Workspaces.objects.get(id=id)

            serializer = serializers.WorkspacesSerializer(workspace, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse("sucess", safe=False)
            
            return JsonResponse(serializer.errors, safe=False)

        except ObjectDoesNotExist:
            return JsonResponse("workspace does not exist", safe=False)


"""
TimeType View Class
"""
class TimeTypeView(APIView):
    
    def get(self, request):
        queryset = TimeType.objects.all()
        workspace_id = request.query_params.get('workspace_id', None)

        if workspace_id is not None :
            queryset = queryset.filter(workspace_id=workspace_id)
        
        timetype_serializer = serializers.TimeTypeSerializer(queryset, many=True)

        return JsonResponse(timetype_serializer.data, safe=False)

    def post(self, request):

        workspace_id = request.data.get("workspace_id", None)

        try:
            workspace = Workspaces.objects.get(id=workspace_id)
        except ObjectDoesNotExist:
            # @dev proper error code here
            return JsonResponse("workspace does not exist", safe=False)

        serializer = serializers.TimeTypeSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(workspace=workspace)
            return JsonResponse("success", safe=False)
        
        # @dev: define error codes properly
        return  JsonResponse(serializer.errors, safe=False)

    # @dev confirm the URL 
    def patch(self, request):
        id = request.data.get("id", None)
        try:
            timetype = TimeType.objects.get(id=id)

            serializer = serializers.TimeTypeSerializer(timetype, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return JsonResponse("success", safe=False)
            
            return JsonResponse(serializer.errors, safe=False)
                
        
        except ObjectDoesNotExist:
            return JsonResponse("workspace does not exist", safe=False)
        

class GpsView(APIView):
    def get(self, request):

        queryset = Gps.objects.all()

        serializer = GpsSerializer(queryset, many=True)

        return JsonResponse(serializer.data, safe=False)

    #POST
    def post(self, request):
        # query filter
        user_id = request.data.get("user_id", None)
        workspace_id = request.data.get("workspace_id", None)
        work_time_period_id = request.data.get("work_time_period_id", None)
        gps_point = request.data.getlist("gps_point", [])
        #timestamp = request.data.get('timestamp', None)

        gps = Gps.objects.create(gps_point=gps_point)

        try:
            if workspace_id is not None:
                workspace = Workspaces.objects.get(id=workspace_id)
                gps.workspace = workspace;

            if work_time_period_id is not None:
                work_time_period = Work_time_period.objects.get(id=work_time_period_id)
                gps.work_time_period = work_time_period
            
            if user_id is not None:
                user = User.objects.get(id=user_id)
                gps.user = user

            gps.save()

            return JsonResponse("success", safe=False)

        except Exception as e:
            return JsonResponse(str(e), safe=False)
    #PATCH
    def patch(self, request):
        # query filter
        id = request.data.get("id", None)
        user_id = request.data.get("user_id", None)
        workspace_id = request.data.get("workspace_id", None)
        work_time_period_id = request.data.get("work_time_period_id", None)
        gps_point = request.data.getlist("gps_point", [])

        try:
            gps = Gps.objects.get(id=id)

            serializer = serializers.GpsSerializer(gps, data=request.data, partial=True)

            workspace = None
            work_time_period = None
            user = None

            if workspace_id is not None:
                workspace = Workspaces.objects.get(id=workspace_id)
                gps.workspace = workspace;

            if work_time_period_id is not None:
                work_time_period = Work_time_period.objects.get(id=work_time_period_id)
                gps.work_time_period = work_time_period
            
            if user_id is not None:
                user = User.objects.get(id=user_id)
                gps.user = user

            if serializer.is_valid():
                serializer.save(
                    workspace = workspace,
                    work_time_period = work_time_period,
                    user = user
                )
                return JsonResponse("success", safe=False)
            
            return JsonResponse(serializer.errors, safe=False)


        except Exception as e:
            return JsonResponse(str(e), safe=False)

"""
Current Gps View
""" 
class CurrentGpsView(APIView):
    # GET
    def get(self, request):
        q = Q()
        workspace_id = request.query_params.get("workspace_id", None)
        user_id = request.query_params.get("user_id", None)
        
        if workspace_id is not None:
            q &= Q(workspace_id=workspace_id)
        
        if user_id is not None:
            q &= Q(user_id=user_id)

        current_gps = Gps.objects.filter(q).order_by('-timestamp')[:1]

        serializer = serializers.GpsSerializer(current_gps, many=True)

        return JsonResponse(serializer.data, safe=False)

"""
Gps Path View
"""
class GpsPathView(APIView):
    # GET
    def get(self, request):
        q = Q()
        user_id = request.query_params.get('user_id', None)
        start_time = request.query_params.get('start_time', None)
        stop_time = request.query_params.get('stop_time', None)
        workspace_id = request.query_params.get('workspace_id', None)

        if user_id is not None:
            q &= Q(user_id = user_id)
        if start_time is not None:
            q &= Q(timestamp__gte = start_time)
        if stop_time is not None:
            q &= Q(timestamp__lte = stop_time)
        if workspace_id is not None:
            q &= Q(workspace_id = workspace_id)
            
        queryset = Gps.objects.filter(q)
        serializer = serializers.GpsSerializer(queryset, many=True)

        return JsonResponse(serializer.data, safe=False)



"""
@api_view(['GET'])
def payroll_report(request):
     params = request.GET
     payroll_time = Payroll_time_period.payroll_time(params)
     data = [ {} for i in range(len(payroll_time))]

     for i in range(len(payroll_time)):
          data[i] = Payroll_time_period.payroll_report(payroll_time[i]["stop_time"], payroll_time[i]["start_time"])
     for i in range(len(data)):
          for j in range(len(data[i])):
               if data[i][j]["start_gps"] != None and data[i][j]["stop_gps"] != None:
                    data[i][j]["distance"] = distance(data[i][j]["start_gps"], data[i][j]["stop_gps"])
               else:
                    data[i][j]["distance"] = 0
     return JsonResponse(data, safe=False)
"""
"""
Payroll Report View
"""
class PayrollReportView(APIView):
    #@dev - pls confirm payrollreport logic
    #@dev - confirm relation between payroll and work time

    #GET
    def get(self, request):
        #get payroll data in time range
        try:
            q = Q()
            
            start_time = request.query_params.get('start_time', None)
            if start_time is not None:
                q &= Q(start_time__gte=datetime.strptime(start_time, "%Y-%m-%d %H:%M"))
            
            stop_time_data = request.query_params.get('stop_time', None)
            if stop_time_data is None or stop_time_data == "":
                stop_time_data = datetime.now().strftime("%Y-%m-%d %H:%M")
            
            stop_time = datetime.strptime(stop_time_data, "%Y-%m-%d %H:%M")
            q &= Q(stop_time__lte=stop_time)

            #approved = request.query_params.get('approved', None)
            #if approved is not None:
            #    q &= Q(approved=approved)
            
            workspace_id = request.query_params.get('workspace_id', None)
            if workspace_id is not None:
                q &= Q(workspace_id=workspace_id)

            user_ids = request.query_params.get('user_ids', [])
            if len(user_ids) > 0:
                q &= Q(user_id__in=user_ids)

            query_time_set = Payroll_time_period.objects.filter(q)

            # payroll_report
            queryset = Work_time_period.objects.select_related('workspace', 'user', 'work', 'timetype').annotate(
                duration=Epoch(F('stop_time')-F('start_time'))
            ).filter(q)

            serializer = serializers.PayrollReportSerializer(queryset, many=True)

            return JsonResponse(serializer.data, safe=False)
        except Exception as e:
            return JsonResponse(str(e), safe=False)


"""
Work Report View
"""
class WorkReportView(APIView):
    def work_report(self, params):
        
        try:
            q = Q()
            start_time = params.get('start_time', None)
            if start_time is not None:
                q &= Q(start_time__gte=datetime.strptime(start_time, "%Y-%m-%d %H:%M"))
            
            stop_time_data = params.get('stop_time', None)
            if stop_time_data is None or stop_time_data == "":
                stop_time_data = datetime.now().strftime("%Y-%m-%d %H:%M")
            
            stop_time = datetime.strptime(stop_time_data, "%Y-%m-%d %H:%M")
            q &= Q(stop_time__lte=stop_time)

            workspace_id = params.get('workspace_id', None)
            if workspace_id is not None:
                q &= Q(workspace_id=workspace_id)
            
            user_ids = params.getlist('user_ids', [])
            if len(user_ids) > 0:
                q &= Q(user_id__in=user_ids)
            
            
            querySet = Work_time_period.objects.select_related('user', 'timetype').annotate(
                duration=Epoch(F('stop_time')-F('start_time'))
            ).filter(q)

            serializer = serializers.WorkReportSerializer(querySet, many=True)
            return serializer.data


        except Exception as e:
            print(str(e))
            return []
    
    #GET
    def get(self, request):
        data = self.work_report(request.query_params)
        return JsonResponse(data, safe=False)

class ActiveTimeView(APIView):
    
    def get_active_time_worktime(self, params):
        queryset = Work_time_period.objects.select_related('timetype').filter(params)
        serializer = serializers.ActiveTimeWorkTimeSerializer(queryset, many=True)
        return serializer.data
    
    def get_active_time_payroll(self, params):
        queryset = Payroll_time_period.objects.select_related('timetype').filter(params)
        serializer = serializers.ActiveTimeWorkPayrollSerializer(queryset)
        return serializer.data

    #GET
    def get(self, request):
        try:
            q = Q()
            workspace_id = request.query_params.get('workspace_id', None)
            if workspace_id is not None:
                q &= Q(workspace_id=workspace_id)
            
            user_id = request.query_params.get('user_id', None)
            if user_id is not None:
                q &= Q(user_id=user_id)
            
            start_time = request.query_params.get('start_time', None)
            if start_time is not None:
                q &= Q(start_time__gte=datetime.strptime(start_time, "%Y-%m-%d %H:%M"))

            data = self.get_active_time_worktime(q)
            if(len(data) == 0):
                data = self.get_active_time_payroll(q)
            
            return JsonResponse(data, safe=False)
        except Exception as e:
            return JsonResponse(str(e), safe=False)
        

"""
Time Utilization View
"""
class TimeUtilizationView(APIView):
    def time_utilization(self, user_id, start_time, stop_time, workspace_id, duration):
        try:
            print(start_time, stop_time)
            q = Q()
            if user_id is not None:
                q &= Q(user_id=user_id)

            if workspace_id is not None:
                q &= Q(workspace_id=workspace_id)
                
            if start_time is not None:
                q &= Q(start_time__gte=start_time)
            
            if stop_time is None or stop_time == "":
                stop_time = datetime.now().strftime("%Y-%m-%d %H:%M")
            
            q &= Q(stop_time__lte=stop_time)

            queryset = Work_time_period.objects.select_related('timetype').annotate(
                duration=Sum(Round((Epoch(F('stop_time')-F('start_time'))) / duration, 2))
            ).filter(q)

            print(queryset.query)

            serializer = serializers.TimeUtilizationWorkTimeSerializer(queryset, many=True)
            print(serializer.data)
            return serializer.data

        except Exception as e:
            print(str(e))
            return []

    #GET
    def get(self, request):
        try:
            q = Q()
            workspace_id = request.query_params.get('workspace_id', None)
            if workspace_id is not None:
                q &= Q(workspace_id=workspace_id)
                
            start_time = request.query_params.get('start_time', None)
            if start_time is not None:
                q &= Q(start_time__gte=datetime.strptime(start_time, "%Y-%m-%d %H:%M"))
            
            stop_time_data = request.query_params.get('stop_time', None)
            if stop_time_data is None or stop_time_data == "":
                stop_time_data = datetime.now().strftime("%Y-%m-%d %H:%M")
            
            stop_time = datetime.strptime(stop_time_data, "%Y-%m-%d %H:%M")
            q &= Q(stop_time__lte=stop_time)

            queryset = Payroll_time_period.objects.annotate(
                payroll_time=Epoch(F('stop_time')-F('start_time'))
            ).filter(q)

            payroll_data = serializers.TimeUtilizationPayrollSerializer(queryset, many=True).data

            data = [{} for i in range(len(payroll_data))]

            for i in range(len(payroll_data)):
                data[i]["user_id"] = payroll_data[i]["user_id"]
                tmp = self.time_utilization(payroll_data[i]["user_id"], payroll_data[i]["start_time"], payroll_data[i]["stop_time"], workspace_id, payroll_data[i]["payroll_time"])
                if tmp:
                    for j in range(len(tmp)):
                        data[i][tmp[j]["name"]] = tmp[j]["duration"]

            return JsonResponse(data, safe = False)




        except Exception as e:
            return JsonResponse(str(e), safe=False)


"""
Time Sheet View
"""
class TimeSheetView(APIView):
    def get(self, request):
        try:
            q = Q()
            start_time = request.query_params.get('start_time', None)
            if start_time is not None:
                q &= Q(start_time__gte=datetime.strptime(start_time, "%Y-%m-%d %H:%M"))
            
            stop_time_data = request.query_params.get('stop_time', None)
            if stop_time_data is None or stop_time_data == "":
                stop_time_data = datetime.now().strftime("%Y-%m-%d %H:%M")
            
            stop_time = datetime.strptime(stop_time_data, "%Y-%m-%d %H:%M")
            q &= Q(stop_time__lte=stop_time)

            #approved = request.query_params.get('approved', None)
            #if approved is not None:
            #    q &= Q(approved=approved)
            
            workspace_id = request.query_params.get('workspace_id', None)
            if workspace_id is not None:
                q &= Q(workspace_id=workspace_id)

            user_ids = request.query_params.get('user_ids', [])
            if len(user_ids) > 0:
                q &= Q(user_id__in=user_ids)

            query_time_sheet = Payroll_time_period.objects.annotate(
                    duration=Epoch(F('stop_time')-F('start_time'))
                ).filter(q)
            
            serializer = serializers.TimeSheetSerializer(query_time_sheet, many=True)

            return JsonResponse(serializer.data, safe=False)
        except Exception as e:
            return JsonResponse(str(e), safe=False)



"""
Work Time Period View
"""
class WorkTimePeriodView(APIView):
    #GET
    def get(self, request):
        try:
            q = Q()
            user_id = request.query_params.get('user_id', None)
            if user_id is not None:
                q &= Q(user_id=user_id)

            workspace_id = request.query_params.get('workspace_id', None)
            if workspace_id is not None:
                q &= Q(workspace_id=workspace_id)

            timetype_id = request.query_params.get('timetype_id', None)
            if timetype_id is not None:
                q &= Q(timetype_id=timetype_id)

            start_time = request.query_params.get('start_time', None)
            if start_time is not None:
                q &= Q(start_time__gte=datetime.strptime(start_time, "%Y-%m-%d %H:%M"))
            
            stop_time_data = request.query_params.get('stop_time', None)
            if stop_time_data is None or stop_time_data == "":
                stop_time_data = datetime.now().strftime("%Y-%m-%d %H:%M");

            stop_time = datetime.strptime(stop_time_data, "%Y-%m-%d %H:%M")
            q &= Q(stop_time__lte=stop_time)

            worktimeQueryset = Work_time_period.objects.filter(q)

            serializer = serializers.WorkTimePeriodSerializer(worktimeQueryset, many=True)
            return JsonResponse(serializer.data, safe=False)
        except Exception as e:
            return JsonResponse(str(e), safe=False)

    #POST
    def post(self, request):
        workspace_id = request.data.get('workspace_id', None)
        user_id = request.data.get('user_id', None)
        timetype_id = request.data.get('timetype_id', None)
        work_id = request.data.get('work_id', None)
    
        try:
            workspace = Workspaces.objects.get(id=workspace_id)
            user = User.objects.get(id=user_id)
            timetype = TimeType.objects.get(id=timetype_id)
            work = Work.objects.get(id=work_id)

            serializer = serializers.WorkTimePeriodSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(
                    workspace=workspace,
                    user=user,
                    timetype=timetype,
                    work=work
                )
                return JsonResponse("success", safe=False)
            
            return JsonResponse(serializer.errors, safe=False)
        
        except Exception as e:
            return JsonResponse(str(e), safe=False)

    #PATCH
    def patch(self, request):
        id = request.data.get('id', None)
        workspace_id = request.data.get('workspace_id', None)
        user_id = request.data.get('user_id', None)
        timetype_id = request.data.get('timetype_id', None)
        work_id = request.data.get('work_id', None)
    
        try:
            queryset = Work_time_period.objects.get(id=id)

            workspace = Workspaces.objects.get(id=workspace_id)
            user = User.objects.get(id=user_id)
            timetype = TimeType.objects.get(id=timetype_id)
            work = Work.objects.get(id=work_id)

            serializer = serializers.WorkTimePeriodSerializer(queryset, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save(
                    workspace=workspace,
                    user=user,
                    timetype=timetype,
                    work=work
                )
                return JsonResponse("success", safe=False)
            
            return JsonResponse(serializer.errors, safe=False)
        
        except Exception as e:
            return JsonResponse(str(e), safe=False)        



"""
Payroll Time Period View
"""
class PayrollTimePeriodView(APIView):
    # add permission to check if user is authenticated
    # permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            q = Q()
            
            user_id = request.query_params.get('user_id', None)
            if user_id is not None:
                q &= Q(user_id=user_id)
            
            workspace_id = request.query_params.get('workspace_id', None)
            if workspace_id is not None:
                q &= Q(workspace_id=workspace_id)
            
            start_time = request.query_params.get('start_time', None)
            if start_time is not None:
                q &= Q(start_time__gte=datetime.strptime(start_time, "%Y-%m-%d %H:%M"))
            
            stop_time_data = request.query_params.get('stop_time', None)
            if stop_time_data is None or stop_time_data == "":
                stop_time_data = datetime.now().strftime("%Y-%m-%d %H:%M");

            stop_time = datetime.strptime(stop_time_data, "%Y-%m-%d %H:%M")
            q &= Q(stop_time__lte=stop_time)

            payrolls = Payroll_time_period.objects.filter(q)

            serializer = serializers.PayrollTimePeriodSerializer(payrolls, many=True)
            return JsonResponse(serializer.data, safe=False)
        except Exception as e:
            return JsonResponse(str(e), safe=False)

    # POST
    # PK
    def post(self, request):
        workspace_id = request.data.get('workspace_id', None)
        user_id = request.data.get('user_id', None)
        
        try:
            workspace = Workspaces.objects.get(id=workspace_id)
            user = User.objects.get(id=user_id)

            serializer = serializers.PayrollTimePeriodSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(
                    workspace=workspace,
                    user=user
                )
                return JsonResponse("success", safe=False)
            
            return JsonResponse(serializer.errors, safe=False)
        
        except Exception as e:
            return JsonResponse(str(e), safe=False)

    # Patch
    # PK
    def patch(self, request):
        id = request.data.get('id', None)

        workspace_id = request.data.get('workspace_id', None)
        user_id = request.data.get('user_id', None)
    
        try:
            payroll = Payroll_time_period.objects.get(id=id)

            workspace = Workspaces.objects.get(id=workspace_id)
            user = User.objects.get(id=user_id)


            serializer = serializers.PayrollTimePeriodSerializer(payroll, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save(
                    workspace=workspace,
                    user=user
                )
                return JsonResponse("success", safe=False)
            
            return JsonResponse(serializer.errors, safe=False)
        
        except Exception as e:
            return JsonResponse(str(e), safe=False)


"""
Crew View
"""
class CrewView(APIView):
    #GET
    def get(self, request):
        q = Q()
        workspace_id = request.query_params.get('workspace_id', None)
        if workspace_id is not None:
            q &= Q(workspace_id = workspace_id)
        active = request.query_params.get('isActive', None)
        if active is not None:
            q &= Q(active = active)
        foreman_user_id = request.query_params.get('foreman_user_id', None)
        if foreman_user_id is not None:
            q &= Q(foreman_user_id = foreman_user_id)
        
        queryset = Crew.objects.filter(q)
        serializer = serializers.CrewSerializer(queryset, many=True)
        return JsonResponse(serializer.data, safe=False)

    #POST
    def post(self, request):
        try:
            workspace_id = request.data.get('workspace_id', None)
            foreman_user_id = request.data.get('foreman_user_id', None)
            crew_name = request.data.get('crew_name', None)
            crew_user_ids = request.data.getlist('crew_user_ids', [])

            workspace = Workspaces.objects.get(id=workspace_id)
            foreman_user = User.objects.get(id=foreman_user_id)

            crew = Crew.objects.create(
                name=crew_name,
                active=False,
                workspace=workspace,
                foreman_user=foreman_user
            )

            for user in crew_user_ids:
                # add exception handling
                crew_user = User.objects.get(id=user)

                if crew_user is not None:
                    crew.crew_users.add(crew_user)
            crew.save()
           
            return JsonResponse("success", safe=False)
           
        except Exception as e:
            return JsonResponse(str(e), safe=False)

    #PATCH
    def patch(self, request):
        try:
            id = request.data.get('id', None)
            workspace_id = request.data.get('workspace_id', None)
            foreman_user_id = request.data.get('foreman_user_id', None)
            crew_name = request.data.get('crew_name', None)
            crew_user_ids = request.data.getlist('crew_user_ids', [])

            workspace = Workspaces.objects.get(id=workspace_id)
            foreman_user = User.objects.get(id=foreman_user_id)

            queryset = Crew.objects.get(id=id)

            crews = queryset.crew_users.all()
            crews.delete()

            for user in crew_user_ids:
                # add exception handling
                crew_user = User.objects.get(id=user)

                if crew_user is not None:
                    queryset.crew_users.add(crew_user)


            serializer = serializers.CrewSerializer(queryset, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save(
                    workspace=workspace,
                    foreman_user=foreman_user
                )

            return JsonResponse("success", safe=False)
           
        except Exception as e:
            return JsonResponse(str(e), safe=False)

"""
User View
"""
class UserView(APIView):
    #GET
    def get(self, request):
        username = request.data.get('username', None)
        print(username)
        if username is None:
            queryset = User.objects.all()
        else:
            queryset = User.objects.get(username=username)

        print(queryset.query)
        
        serializer = serializers.UserSerializer(queryset, many=True)

        return JsonResponse(serializer.data, safe=False)


    #POST
    def post(self, request):
        try:
            user = User.objects.create_user(
                username=request.data.get('username'),
                password=request.data.get('password'),
                email=request.data.get('email'))
            #user.save()
            return JsonResponse("success", safe=False)
        except Exception as e:
            return JsonResponse(str(e), safe=False)

    #PATCH
    def patch(self, request):
        username = request.data.get('username', None)
        if username is None:
            return JsonResponse("username is invalid", safe=False)
        try:
            user = User.objects.get(username=username)
            serializer = serializers.UserSerializer(user, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse("success", safe=False)
            
            return JsonResponse(serializer.errors, safe=False)
        except Exception as e:
            return JsonResponse(str(e), safe=False)
        

"""
Work View
"""
class WorkView(APIView):
    #GET
    def get(self, request):
        q = Q()
        user_id = request.query_params.get('user_id', None)
        if user_id is not None:
            q &= Q(user_id=user_id)

        name = request.query_params.get('name', None)
        if name is not None:
            q &= Q(name=name)

        payroll_time_period_id = request.query_params.get('payroll_time_period_id', None)
        if payroll_time_period_id is not None:
            q &= Q(payroll_time_period_id=payroll_time_period_id)

        workspace_id = request.query_params.get('workspace_id', None)
        if workspace_id is not None:
            q &= Q(workspace_id=workspace_id)

        queryset = Work.objects.filter(q)

        serializer = serializers.WorkSerializer(queryset, many=True)

        return JsonResponse(serializer.data, safe=False)

    #POST
    def post(self, request):
        try:
            user_id = request.data.get('user_id', None)
            payroll_time_period_id = request.data.get('payroll_time_period_id', None)
            workspace_id = request.data.get('workspace_id', None)

            user = User.objects.get(id=user_id)
            payroll = Payroll_time_period.objects.get(id=payroll_time_period_id)
            workspace = Workspaces.objects.get(id=workspace_id)

            serializer = serializers.WorkSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save(
                    user=user,
                    payroll_time_period=payroll,
                    workspace=workspace
                )
                return JsonResponse("success", safe=False)
            
            return JsonResponse(serializer.errors, safe=False)
        
        except Exception as e:
            return JsonResponse(str(e), safe=False)

    #PATCH
    def patch(self, request):
        try:
            id = request.data.get("id", None)
            work = Work.objects.get(id=id)

            user_id = request.data.get('user_id', None)
            payroll_time_period_id = request.data.get('payroll_time_period_id', None)
            workspace_id = request.data.get('workspace_id', None)

            user = User.objects.get(id=user_id)
            payroll = Payroll_time_period.objects.get(id=payroll_time_period_id)
            workspace = Workspaces.objects.get(id=workspace_id)

            serializer = serializers.WorkSerializer(work, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save(
                    user=user,
                    payroll_time_period=payroll,
                    workspace=workspace
                )
                return JsonResponse("success", safe=False)
            
            return JsonResponse(serializer.errors, safe=False)
        
        except Exception as e:
            return JsonResponse(str(e), safe=False)

