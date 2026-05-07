"""
Views for the Task Delegation and Employee Monitoring Portal.
Includes authentication, dashboards, task management, AJAX endpoints,
admin user management, and performance reports.
"""

import json
from functools import wraps

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q, Count
from django.core.paginator import Paginator

from .models import User, Task, ActivityLog, Notification
from .forms import (
    UserRegistrationForm, UserLoginForm, TaskForm,
    TaskStatusForm, AdminUserForm, ProfileForm,
)


# ---------------------------------------------------------------------------
# Decorators
# ---------------------------------------------------------------------------

def role_required(*roles):
    """Decorator to restrict views to certain user roles."""
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if request.user.role not in roles:
                messages.error(request, 'You do not have permission to access this page.')
                return redirect('dashboard')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


# ---------------------------------------------------------------------------
# Authentication Views
# ---------------------------------------------------------------------------

def register_view(request):
    """Handle new user registration."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome, {user.first_name}! Your account has been created.')
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    """Handle user login."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect('dashboard')
    else:
        form = UserLoginForm()
    return render(request, 'registration/login.html', {'form': form})


def logout_view(request):
    """Log the user out and redirect to login."""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


@login_required
def profile_view(request):
    """Allow users to view / edit their profile."""
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'core/profile.html', {'form': form})


# ---------------------------------------------------------------------------
# Dashboard Views
# ---------------------------------------------------------------------------

@login_required
def dashboard(request):
    """Route users to their role-specific dashboard."""
    if request.user.is_admin_user:
        return admin_dashboard(request)
    elif request.user.is_manager:
        return manager_dashboard(request)
    else:
        return employee_dashboard(request)


def admin_dashboard(request):
    """Admin dashboard — system overview and user stats."""
    total_users = User.objects.count()
    total_tasks = Task.objects.count()
    total_managers = User.objects.filter(role='manager').count()
    total_employees = User.objects.filter(role='employee').count()
    pending_tasks = Task.objects.filter(status='pending').count()
    in_progress_tasks = Task.objects.filter(status='in_progress').count()
    completed_tasks = Task.objects.filter(status='completed').count()
    recent_tasks = Task.objects.all()[:10]
    recent_logs = ActivityLog.objects.all()[:10]
    context = {
        'total_users': total_users,
        'total_tasks': total_tasks,
        'total_managers': total_managers,
        'total_employees': total_employees,
        'pending_tasks': pending_tasks,
        'in_progress_tasks': in_progress_tasks,
        'completed_tasks': completed_tasks,
        'recent_tasks': recent_tasks,
        'recent_logs': recent_logs,
    }
    return render(request, 'core/admin_dashboard.html', context)


def manager_dashboard(request):
    """Manager dashboard — tasks created and employee progress."""
    my_tasks = Task.objects.filter(assigned_by=request.user)
    total = my_tasks.count()
    pending = my_tasks.filter(status='pending').count()
    in_progress = my_tasks.filter(status='in_progress').count()
    completed = my_tasks.filter(status='completed').count()

    # Employee performance summary
    employees = User.objects.filter(role='employee')
    employee_stats = []
    for emp in employees:
        emp_tasks = Task.objects.filter(assigned_to=emp)
        employee_stats.append({
            'employee': emp,
            'total': emp_tasks.count(),
            'pending': emp_tasks.filter(status='pending').count(),
            'in_progress': emp_tasks.filter(status='in_progress').count(),
            'completed': emp_tasks.filter(status='completed').count(),
        })

    recent_tasks = my_tasks[:10]
    context = {
        'total': total,
        'pending': pending,
        'in_progress': in_progress,
        'completed': completed,
        'recent_tasks': recent_tasks,
        'employee_stats': employee_stats,
    }
    return render(request, 'core/manager_dashboard.html', context)


def employee_dashboard(request):
    """Employee dashboard — assigned tasks and progress summary."""
    my_tasks = Task.objects.filter(assigned_to=request.user)
    total = my_tasks.count()
    pending = my_tasks.filter(status='pending').count()
    in_progress = my_tasks.filter(status='in_progress').count()
    completed = my_tasks.filter(status='completed').count()
    overdue = sum(1 for t in my_tasks if t.is_overdue)
    recent_tasks = my_tasks[:10]
    context = {
        'total': total,
        'pending': pending,
        'in_progress': in_progress,
        'completed': completed,
        'overdue': overdue,
        'recent_tasks': recent_tasks,
    }
    return render(request, 'core/employee_dashboard.html', context)


# ---------------------------------------------------------------------------
# Task CRUD Views
# ---------------------------------------------------------------------------

@login_required
def task_list(request):
    """List tasks with search, filter, and pagination."""
    if request.user.is_admin_user:
        tasks = Task.objects.all()
    elif request.user.is_manager:
        tasks = Task.objects.filter(assigned_by=request.user)
    else:
        tasks = Task.objects.filter(assigned_to=request.user)

    # Search
    query = request.GET.get('q', '')
    if query:
        tasks = tasks.filter(Q(title__icontains=query) | Q(description__icontains=query))

    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        tasks = tasks.filter(status=status_filter)

    # Filter by priority
    priority_filter = request.GET.get('priority', '')
    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)

    # Pagination
    paginator = Paginator(tasks, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'query': query,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
    }
    return render(request, 'core/task_list.html', context)


@role_required('manager')
def task_create(request):
    """Allow managers to create a new task."""
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.assigned_by = request.user
            task.save()

            # Create activity log
            ActivityLog.objects.create(
                task=task, user=request.user,
                action=f'Task "{task.title}" created and assigned to {task.assigned_to.username}',
                new_status='pending',
            )

            # Notify the employee
            Notification.objects.create(
                user=task.assigned_to,
                message=f'New task assigned: {task.title}',
                link=f'/tasks/{task.pk}/',
            )

            messages.success(request, 'Task created successfully.')
            return redirect('task_list')
    else:
        form = TaskForm()
    return render(request, 'core/task_form.html', {'form': form, 'title': 'Create Task'})


@role_required('manager')
def task_edit(request, pk):
    """Allow managers to edit an existing task."""
    task = get_object_or_404(Task, pk=pk, assigned_by=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            ActivityLog.objects.create(
                task=task, user=request.user,
                action=f'Task "{task.title}" updated by {request.user.username}',
            )
            messages.success(request, 'Task updated successfully.')
            return redirect('task_detail', pk=task.pk)
    else:
        form = TaskForm(instance=task)
    return render(request, 'core/task_form.html', {'form': form, 'title': 'Edit Task'})


@role_required('manager')
def task_delete(request, pk):
    """Allow managers to delete a task."""
    task = get_object_or_404(Task, pk=pk, assigned_by=request.user)
    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Task deleted successfully.')
        return redirect('task_list')
    return render(request, 'core/task_confirm_delete.html', {'task': task})


@login_required
def task_detail(request, pk):
    """View task details and activity log."""
    task = get_object_or_404(Task, pk=pk)

    # Access control
    if not (request.user.is_admin_user or
            task.assigned_by == request.user or
            task.assigned_to == request.user):
        messages.error(request, 'You do not have permission to view this task.')
        return redirect('dashboard')

    # Employee status update
    status_form = None
    if request.user.is_employee and task.assigned_to == request.user:
        if request.method == 'POST':
            status_form = TaskStatusForm(request.POST)
            if status_form.is_valid():
                old_status = task.status
                new_status = status_form.cleaned_data['status']
                task.status = new_status

                if new_status == 'completed' and old_status != 'completed':
                    task.completed_at = timezone.now()
                elif new_status != 'completed':
                    task.completed_at = None

                task.save()

                ActivityLog.objects.create(
                    task=task, user=request.user,
                    action=f'Status changed from {old_status} to {new_status}',
                    old_status=old_status, new_status=new_status,
                )

                # Notify the manager
                Notification.objects.create(
                    user=task.assigned_by,
                    message=f'{request.user.username} updated "{task.title}" to {new_status}',
                    link=f'/tasks/{task.pk}/',
                )

                messages.success(request, 'Task status updated.')
                return redirect('task_detail', pk=task.pk)
        else:
            status_form = TaskStatusForm(initial={'status': task.status})

    logs = task.activity_logs.all()
    context = {
        'task': task,
        'status_form': status_form,
        'logs': logs,
    }
    return render(request, 'core/task_detail.html', context)


# ---------------------------------------------------------------------------
# AJAX Endpoints — Real-Time Updates
# ---------------------------------------------------------------------------

@login_required
def ajax_task_updates(request):
    """Return task updates as JSON for real-time polling."""
    if request.user.is_admin_user:
        tasks = Task.objects.all()
    elif request.user.is_manager:
        tasks = Task.objects.filter(assigned_by=request.user)
    else:
        tasks = Task.objects.filter(assigned_to=request.user)

    data = []
    for t in tasks[:50]:
        data.append({
            'id': t.pk,
            'title': t.title,
            'status': t.status,
            'status_display': t.get_status_display(),
            'priority': t.priority,
            'priority_display': t.get_priority_display(),
            'assigned_to': t.assigned_to.get_full_name() or t.assigned_to.username,
            'assigned_by': t.assigned_by.get_full_name() or t.assigned_by.username,
            'deadline': t.deadline.strftime('%Y-%m-%d %H:%M'),
            'is_overdue': t.is_overdue,
            'updated_at': t.updated_at.strftime('%Y-%m-%d %H:%M'),
        })
    return JsonResponse({'tasks': data})


@login_required
def ajax_task_status_update(request, pk):
    """AJAX endpoint for employees to update task status."""
    if request.method == 'POST':
        task = get_object_or_404(Task, pk=pk, assigned_to=request.user)
        try:
            body = json.loads(request.body)
            new_status = body.get('status')
        except (json.JSONDecodeError, AttributeError):
            new_status = request.POST.get('status')

        if new_status not in ['pending', 'in_progress', 'completed']:
            return JsonResponse({'error': 'Invalid status'}, status=400)

        old_status = task.status
        task.status = new_status

        if new_status == 'completed' and old_status != 'completed':
            task.completed_at = timezone.now()
        elif new_status != 'completed':
            task.completed_at = None

        task.save()

        ActivityLog.objects.create(
            task=task, user=request.user,
            action=f'Status changed from {old_status} to {new_status}',
            old_status=old_status, new_status=new_status,
        )

        Notification.objects.create(
            user=task.assigned_by,
            message=f'{request.user.username} updated "{task.title}" to {new_status}',
            link=f'/tasks/{task.pk}/',
        )

        return JsonResponse({
            'success': True,
            'new_status': new_status,
            'new_status_display': task.get_status_display(),
        })

    return JsonResponse({'error': 'POST required'}, status=405)


@login_required
def ajax_notifications(request):
    """Return unread notifications as JSON."""
    notifs = Notification.objects.filter(user=request.user, is_read=False)[:20]
    data = [{
        'id': n.pk,
        'message': n.message,
        'link': n.link,
        'created_at': n.created_at.strftime('%Y-%m-%d %H:%M'),
    } for n in notifs]
    return JsonResponse({'notifications': data, 'count': notifs.count()})


@login_required
def ajax_mark_notification_read(request, pk):
    """Mark a notification as read."""
    if request.method == 'POST':
        notif = get_object_or_404(Notification, pk=pk, user=request.user)
        notif.is_read = True
        notif.save()
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'POST required'}, status=405)


@login_required
def ajax_mark_all_read(request):
    """Mark all notifications as read."""
    if request.method == 'POST':
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'POST required'}, status=405)


# ---------------------------------------------------------------------------
# Admin User Management
# ---------------------------------------------------------------------------

@role_required('admin')
def admin_user_list(request):
    """Admin view to list all users."""
    users = User.objects.all().order_by('role', 'username')
    query = request.GET.get('q', '')
    if query:
        users = users.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        )
    paginator = Paginator(users, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'core/admin_user_list.html', {'page_obj': page_obj, 'query': query})


@role_required('admin')
def admin_user_create(request):
    """Admin view to create a new user."""
    if request.method == 'POST':
        form = AdminUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data.get('password')
            if password:
                user.set_password(password)
            else:
                user.set_password('changeme123')
            user.save()
            messages.success(request, f'User {user.username} created successfully.')
            return redirect('admin_user_list')
    else:
        form = AdminUserForm()
    return render(request, 'core/admin_user_form.html', {'form': form, 'title': 'Create User'})


@role_required('admin')
def admin_user_edit(request, pk):
    """Admin view to edit an existing user."""
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = AdminUserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f'User {user.username} updated successfully.')
            return redirect('admin_user_list')
    else:
        form = AdminUserForm(instance=user)
    return render(request, 'core/admin_user_form.html', {'form': form, 'title': f'Edit User: {user.username}'})


@role_required('admin')
def admin_user_delete(request, pk):
    """Admin view to delete a user."""
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.delete()
        messages.success(request, f'User {user.username} deleted successfully.')
        return redirect('admin_user_list')
    return render(request, 'core/admin_user_confirm_delete.html', {'target_user': user})


# ---------------------------------------------------------------------------
# Performance Reports
# ---------------------------------------------------------------------------

@login_required
def performance_report(request):
    """Show performance metrics and reports."""
    if request.user.is_employee:
        tasks = Task.objects.filter(assigned_to=request.user)
    elif request.user.is_manager:
        tasks = Task.objects.filter(assigned_by=request.user)
    else:
        tasks = Task.objects.all()

    total = tasks.count()
    completed = tasks.filter(status='completed').count()
    pending = tasks.filter(status='pending').count()
    in_progress = tasks.filter(status='in_progress').count()
    overdue = sum(1 for t in tasks if t.is_overdue)

    # Efficiency: % tasks completed on time
    completed_tasks = tasks.filter(status='completed', completed_at__isnull=False)
    on_time = sum(1 for t in completed_tasks if t.completed_at <= t.deadline)
    efficiency = round((on_time / completed) * 100, 1) if completed > 0 else 0

    # Average completion time
    durations = [t.time_to_complete for t in completed_tasks if t.time_to_complete]
    if durations:
        avg_seconds = sum(d.total_seconds() for d in durations) / len(durations)
        avg_hours = round(avg_seconds / 3600, 1)
    else:
        avg_hours = 0

    # Per-employee stats (for manager/admin)
    employee_report = []
    if request.user.is_manager or request.user.is_admin_user:
        employees = User.objects.filter(role='employee')
        for emp in employees:
            emp_tasks = Task.objects.filter(assigned_to=emp)
            emp_completed = emp_tasks.filter(status='completed').count()
            emp_total = emp_tasks.count()
            employee_report.append({
                'employee': emp,
                'total': emp_total,
                'completed': emp_completed,
                'pending': emp_tasks.filter(status='pending').count(),
                'in_progress': emp_tasks.filter(status='in_progress').count(),
                'completion_rate': round((emp_completed / emp_total) * 100, 1) if emp_total > 0 else 0,
            })

    context = {
        'total': total,
        'completed': completed,
        'pending': pending,
        'in_progress': in_progress,
        'overdue': overdue,
        'efficiency': efficiency,
        'avg_hours': avg_hours,
        'employee_report': employee_report,
    }
    return render(request, 'core/performance_report.html', context)
