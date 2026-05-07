"""
URL configuration for the core app.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),

    # Dashboard
    path('', views.dashboard, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Task management
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/create/', views.task_create, name='task_create'),
    path('tasks/<int:pk>/', views.task_detail, name='task_detail'),
    path('tasks/<int:pk>/edit/', views.task_edit, name='task_edit'),
    path('tasks/<int:pk>/delete/', views.task_delete, name='task_delete'),

    # AJAX endpoints
    path('api/tasks/', views.ajax_task_updates, name='ajax_task_updates'),
    path('api/tasks/<int:pk>/status/', views.ajax_task_status_update, name='ajax_task_status_update'),
    path('api/notifications/', views.ajax_notifications, name='ajax_notifications'),
    path('api/notifications/<int:pk>/read/', views.ajax_mark_notification_read, name='ajax_mark_notification_read'),
    path('api/notifications/mark-all-read/', views.ajax_mark_all_read, name='ajax_mark_all_read'),

    # Admin user management
    path('users/', views.admin_user_list, name='admin_user_list'),
    path('users/create/', views.admin_user_create, name='admin_user_create'),
    path('users/<int:pk>/edit/', views.admin_user_edit, name='admin_user_edit'),
    path('users/<int:pk>/delete/', views.admin_user_delete, name='admin_user_delete'),

    # Reports
    path('reports/', views.performance_report, name='performance_report'),
]
