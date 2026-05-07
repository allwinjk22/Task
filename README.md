# Real-Time Task Delegation and Employee Monitoring Portal

A full-stack web application built with **Django** and **SQLite** that supports role-based task management, real-time monitoring, and performance analytics.

## Features

- **Three user roles**: Admin, Manager, Employee with role-based access control
- **Task management**: Create, assign, edit, delete, and track tasks with deadlines and priorities
- **Real-time updates**: AJAX polling for live task status and notification updates
- **Dashboards**: Role-specific dashboards with key metrics and activity feeds
- **Performance reports**: Completion rates, on-time delivery, and per-employee analytics with Chart.js
- **Notifications**: In-app notification system with bell icon and dropdown
- **Search & filter**: Search tasks by title/description, filter by status and priority
- **Pagination**: Paginated task and user lists
- **Responsive UI**: Bootstrap 5 dark theme with glassmorphism design

## Tech Stack

| Layer     | Technology                          |
|-----------|-------------------------------------|
| Backend   | Python, Django 6.x                  |
| Database  | SQLite                              |
| Frontend  | HTML5, CSS3, Bootstrap 5, Chart.js  |
| Real-Time | AJAX (Fetch API) with polling       |

## Setup Instructions

### Prerequisites
- Python 3.10 or higher

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Run Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 3: Create a Superuser (Admin Account)

```bash
python manage.py createsuperuser
```
When prompted, choose a username and password. Set the role to `admin` in the Django admin panel after creation.

### Step 4: Run the Development Server

```bash
python manage.py runserver
```

### Step 5: Access the Application

Open your browser and go to: **http://127.0.0.1:8000/**

- Register as a **Manager** or **Employee** via the registration page
- Login to access your role-specific dashboard
- Use the Django admin panel at **http://127.0.0.1:8000/admin/** for advanced user management

## Project Structure

```
├── manage.py                   # Django management script
├── requirements.txt            # Python dependencies
├── taskportal/                 # Project configuration
│   ├── settings.py             # Django settings
│   ├── urls.py                 # Root URL configuration
│   └── wsgi.py                 # WSGI entry point
├── core/                       # Main application
│   ├── models.py               # User, Task, ActivityLog, Notification models
│   ├── views.py                # All views (auth, dashboards, CRUD, AJAX, reports)
│   ├── forms.py                # Django forms for all features
│   ├── urls.py                 # App URL patterns
│   ├── admin.py                # Django admin registration
│   ├── context_processors.py   # Notification count context processor
│   ├── templates/              # HTML templates
│   │   ├── base.html           # Base layout with navbar
│   │   ├── registration/       # Login & register pages
│   │   └── core/               # Dashboard, task, user, report templates
│   └── static/core/            # Static assets
│       ├── css/style.css       # Custom dark theme CSS
│       └── js/main.js          # AJAX polling & interactions
└── db.sqlite3                  # SQLite database (auto-created)
```

## User Roles

| Role     | Capabilities                                                    |
|----------|-----------------------------------------------------------------|
| Admin    | Manage all users, view all tasks, system overview dashboard     |
| Manager  | Create/assign/edit/delete tasks, monitor employee performance   |
| Employee | View assigned tasks, update task status, view personal progress |

## License

This project is for educational purposes — MCA final-year project.
