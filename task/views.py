from django.shortcuts import render
from accounts.models import User
from .models import *
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Create your views here.

@login_required
def dashboard_page(request):
    login_user_object = request.user
    user_type = login_user_object.user_type
    name = f'{login_user_object.first_name} {login_user_object.last_name}'
    current_date = datetime.date.today().isoformat()
    attendance_object = Attendance.objects.filter(user=login_user_object).first()
    if attendance_object is not None:
        attendance_dict = attendance_object.attendance_detail
    if attendance_object == None or current_date not in attendance_dict['start_time'] or (current_date in attendance_dict['end_time'] and len(attendance_dict['start_time'][current_date]) == len(attendance_dict['end_time'][current_date] )) :
        action_str = 'start'
    else:
        action_str = 'end'
    
    # This condition exiqute when user type is Employee
    if user_type == 'Employee':
        employee_task_details = EmployeeTask.objects.filter(user=login_user_object)
        current_date = datetime.datetime.fromisoformat(current_date).date()
        context = {'employee_task_details':employee_task_details,
                    'current_date':current_date, 'name':name,
                    'action_str':action_str, 'user_type':user_type }
    
    # This condition exiqute when user type is Manager
    else:
        if request.method == 'POST':
            project_name = request.POST.get('project_name')
            Project.objects.create(project_name=project_name,user=login_user_object)
            target_url = reverse('dashboard_page')
            return HttpResponseRedirect(target_url)
        project_details = Project.objects.filter(user=login_user_object)
        context = { 'project_details':project_details, 
                'name':name, 'action_str':action_str,
                'user_type':user_type }
    return render(request, 'task/dashboard.html', context)

@login_required
def employee_task_action(request, employee_id, action):
    current_datetime = datetime.datetime.now()
    if action == 'start':
        EmployeeTask.objects.filter(id=employee_id).update(task_start_date=current_datetime, task_end_date=None)
    else:
        EmployeeTask.objects.filter(id=employee_id).update(task_end_date=current_datetime)
    return HttpResponseRedirect(reverse('dashboard_page'))

@login_required
def massage_page(request, employee_task_id):
    login_user_object = request.user
    username = login_user_object.username
    user_type = login_user_object.user_type
    massage_object = Massage.objects.filter(employee_task=employee_task_id).first()
    if massage_object == None:
        employee_object = EmployeeTask.objects.filter(id = employee_task_id).first()
        if employee_object is not None:
            massage_object = Massage.objects.create(employee_task=employee_object)
    if request.method == 'POST':
        massage = request.POST.get('massage')
        current_datetime_str =  datetime.datetime.now().isoformat()
        massage_detail_dict = {'massage':massage, 'date_time':current_datetime_str, 'username':username} 
        massage_object.massage_detail.append(massage_detail_dict)
        massage_object.save()
        target_url = reverse('massage_page', args=[employee_task_id])
        return HttpResponseRedirect(target_url)
    context = {'massage_object':massage_object, 'username':username, 'user_type':user_type}
    return render(request, 'task/massage.html', context)

@login_required
def attendance_action(request, action):
    login_user_object = request.user
    current_date = datetime.date.today().isoformat()
    current_datetime =  datetime.datetime.now().isoformat()
    attendance_object = Attendance.objects.filter(user=login_user_object).first()
    if attendance_object == None:
        attendance_object = Attendance.objects.create(user=login_user_object, attendance_detail={'start_time':{},'end_time':{}})
    if action == 'start':
        if current_date in attendance_object.attendance_detail['start_time']:
            ## here current date key is exist in dictionary.
            attendance_object.attendance_detail['start_time'][current_date].append(current_datetime)
        else:
            ## here current date key is not exist in dictionary.
            attendance_object.attendance_detail['start_time'][current_date] = [current_datetime]
    else:
        if current_date in attendance_object.attendance_detail['end_time']:
            attendance_object.attendance_detail['end_time'][current_date].append(current_datetime)
        else:
            attendance_object.attendance_detail['end_time'][current_date] = [current_datetime]
    attendance_object.save()
    return HttpResponseRedirect(reverse('dashboard_page'))

@login_required
def delete_project(request, project_id):
    project_object = Project.objects.get(id=project_id)
    project_object.delete()
    messages.error(request, 'Project delete successfully')
    return HttpResponseRedirect(reverse('dashboard_page'))

@login_required
def delete_manager_task(request, manager_task_id):
    manager_task_object = ManagerTask.objects.get(id=manager_task_id)
    project_id = manager_task_object.project.id
    manager_task_object.delete()
    messages.error(request, 'Task delete successfully')
    target_url = reverse('manager_task', args=[project_id])
    return HttpResponseRedirect(target_url)

@login_required
def manager_task(request, project_id):
    if request.method == 'POST':
        operation = request.POST.get('operation')
        if operation == "add task":
            task_name = request.POST.get('task_name')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            assign = request.POST.get('assign')
            user_object = User.objects.filter(username=assign, user_type='Employee').first()
            if user_object is None:
                messages.error(request, 'incorrect Assign name as username')
                target_url = reverse('manager_task', args=[project_id])
                return HttpResponseRedirect(target_url)
            project_object = Project.objects.filter(id=project_id).first()
            if project_object is not None :
                if ManagerTask.objects.filter(task_name=task_name, project=project_id).first() == None: 
                    manager_task_object = ManagerTask.objects.create(
                        task_name=task_name,
                        start_date=start_date,
                        end_date=end_date,
                        assign=assign,
                        project=project_object
                    )
                    EmployeeTask.objects.create(
                        user=user_object,
                        manager_task=manager_task_object
                    )    
                else:
                    messages.error(request, 'This task name already exit in project. so you can not add.')   
            target_url = reverse('manager_task', args=[project_id])
            return HttpResponseRedirect(target_url)
        else:
            employee_username = request.POST.get('employee_username')
            user_object = User.objects.filter(username=employee_username, user_type='Employee').first()
            if user_object is None:
                messages.error(request, 'Please provide correct employee username')
                target_url = reverse('manager_task', args=[project_id])
                return HttpResponseRedirect(target_url)
            employee_task_details = EmployeeTask.objects.filter(manager_task__project=project_id, manager_task__assign=employee_username )
            project_name = Project.objects.get(id=project_id).project_name
            context = {'employee_task_details':employee_task_details,
                        'project_id':project_id, 'Go_dashboard':False, 
                        'project_name':project_name }
            return render(request, 'task/manager_task.html', context)
    employee_task_details = EmployeeTask.objects.filter(manager_task__project=project_id)
    project_name = Project.objects.get(id=project_id).project_name
    context = {'employee_task_details':employee_task_details, 
                'Go_dashboard':True, 
                'project_name':project_name}
    return render(request, 'task/manager_task.html', context)
