
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login, name = 'login'),
    path('logout/', views.logout, name='logout'),
    path('time-keeping/', views.time_keeping, name='time-keeping'),
    path('timesheet/<str:username>/', views.timesheet, name='timesheet'),
    path('profile/<str:username>/', views.profile_detail, name='profile-detail'),
    path('complaint/', views.complaint, name='complaint'),
    path('complaint/<int:id>/', views.complaint_detail, name='complaint-detail'),
    path('request-absence/<str:username>/', views.request_absence, name='request-absence'),
]
