from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='manager'),
    path('employee/', views.employee, name='employee'),
    path('employee/create/', views.create_employee, name='create-employee'),
    path('employee/update/<str:username>/', views.update_employee, name='create-employee'),
    path('timesheet/', views.main_timesheet, name='main-timesheet'),
    path('salary/', views.total_salary, name='total-salary'),
    path('complaint/', views.complaint, name='complaint'),
    path('absence/', views.absence_review, name='absence'),
]