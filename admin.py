from django.contrib import admin
from .models import UserProfile, IncidentReport, Notification

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'phone']
    list_filter = ['role']
    search_fields = ['user__username', 'user__email']

@admin.register(IncidentReport)
class IncidentReportAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'status', 'reporter', 'location', 'created_at']
    list_filter = ['category', 'status', 'created_at']
    search_fields = ['title', 'description', 'location']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'message', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['user__username', 'message']