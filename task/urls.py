from django.urls import path
from . import views
urlpatterns = [
    path('dashboard/', views.dashboard_page, name='dashboard_page'),
    path('employee-task-action/<int:employee_id>/<str:action>/', views.employee_task_action, name='employee_task_action'),
    path('manager-task/<int:project_id>/', views.manager_task, name='manager_task'),
    path('delete-project/<int:project_id>/', views.delete_project, name='delete_project'),
    path('delete-task/<int:manager_task_id>/', views.delete_manager_task, name='delete_manager_task'),
    path('massage/<int:employee_task_id>/', views.massage_page, name='massage_page'),
    path('attendance/<str:action>/', views.attendance_action, name='attendance_action'),
]
