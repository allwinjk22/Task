"""
Register core models with Django admin.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Task, ActivityLog, Notification


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Admin config for the custom User model."""
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active')
    list_filter = ('role', 'is_active', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'phone', 'department')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('role', 'phone', 'department')}),
    )


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'assigned_by', 'assigned_to', 'status', 'priority', 'deadline', 'created_at')
    list_filter = ('status', 'priority')
    search_fields = ('title', 'description')


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('task', 'user', 'action', 'timestamp')
    list_filter = ('timestamp',)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'is_read', 'created_at')
    list_filter = ('is_read',)
