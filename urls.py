from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'emergency'

urlpatterns = [
    path('', views.CustomLoginView.as_view(), name='login'),
    path('register/', views.register_view, name='guidelines'),
    path('logout/', views.custom_logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),

    path('student/', views.student_dashboard, name='student_dashboard'),
    path('fire/', views.fire_dashboard, name='fire_dashboard'),
    path('health/', views.health_dashboard, name='health_dashboard'),
    path('social/', views.social_dashboard, name='social_dashboard'),
    path('dashboard_admin/', views.admin_dashboard, name='admin_dashboard'),
    
    path('incident/<int:incident_id>/', views.incident_detail, name='incident_detail'),
    path('incident/<int:incident_id>/update/', views.update_incident_status, name='update_incident_status'),
    
    path('api/notifications/', views.get_notifications, name='get_notifications'),
    path('api/notifications/mark-read/', views.mark_notifications_read, name='mark_notifications_read'),
]