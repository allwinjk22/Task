"""
Models for the Task Delegation and Employee Monitoring Portal.
Defines User, Task, ActivityLog, and Notification models.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    """Custom user model with role-based access control."""

    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('employee', 'Employee'),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='employee')
    phone = models.CharField(max_length=15, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    @property
    def is_admin_user(self):
        return self.role == 'admin'

    @property
    def is_manager(self):
        return self.role == 'manager'

    @property
    def is_employee(self):
        return self.role == 'employee'


class Task(models.Model):
    """Task model for task delegation and tracking."""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    deadline = models.DateTimeField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')

    assigned_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='tasks_assigned'
    )
    assigned_to = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='tasks_received'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def is_overdue(self):
        """Check if the task is past its deadline and not completed."""
        if self.status != 'completed' and self.deadline < timezone.now():
            return True
        return False

    @property
    def time_to_complete(self):
        """Return the duration taken to complete a task, or None."""
        if self.completed_at:
            return self.completed_at - self.created_at
        return None


class ActivityLog(models.Model):
    """Tracks every status change or action performed on a task."""

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='activity_logs')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs')
    action = models.CharField(max_length=255)
    old_status = models.CharField(max_length=15, blank=True, null=True)
    new_status = models.CharField(max_length=15, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.username} — {self.action} — {self.task.title}"


class Notification(models.Model):
    """In-app notifications for users."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=500)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    link = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message[:50]}"
