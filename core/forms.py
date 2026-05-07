"""
Forms for the Task Delegation and Employee Monitoring Portal.
Includes registration, login, task management, and user administration forms.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Task


class UserRegistrationForm(UserCreationForm):
    """Form for new user registration."""

    email = forms.EmailField(required=True, widget=forms.EmailInput(
        attrs={'class': 'form-control', 'placeholder': 'Email address'}
    ))
    first_name = forms.CharField(max_length=30, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'First name'}
    ))
    last_name = forms.CharField(max_length=30, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Last name'}
    ))
    role = forms.ChoiceField(choices=[
        ('employee', 'Employee'),
        ('manager', 'Manager'),
    ], widget=forms.Select(attrs={'class': 'form-select'}))
    department = forms.CharField(max_length=100, required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Department'}
    ))
    phone = forms.CharField(max_length=15, required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Phone number'}
    ))

    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'role', 'department', 'phone', 'password1', 'password2',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control', 'placeholder': 'Username'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control', 'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control', 'placeholder': 'Confirm password'
        })


class UserLoginForm(AuthenticationForm):
    """Custom styled login form."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control', 'placeholder': 'Username'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control', 'placeholder': 'Password'
        })


class TaskForm(forms.ModelForm):
    """Form for Managers to create or edit tasks."""

    deadline = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={'class': 'form-control', 'type': 'datetime-local'},
            format='%Y-%m-%dT%H:%M',
        ),
        input_formats=['%Y-%m-%dT%H:%M'],
    )

    class Meta:
        model = Task
        fields = ['title', 'description', 'deadline', 'priority', 'assigned_to']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Task title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Task description'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only allow assigning tasks to employees
        self.fields['assigned_to'].queryset = User.objects.filter(role='employee')
        self.fields['assigned_to'].label = 'Assign To (Employee)'


class TaskStatusForm(forms.Form):
    """Form for Employees to update task status."""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )


class AdminUserForm(forms.ModelForm):
    """Form for Admin to create or edit users."""

    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Leave blank to keep current password'}),
        help_text='Leave blank to keep the current password (edit mode).',
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 'department', 'phone', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
    """Form for users to edit their own profile."""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'department']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
        }
