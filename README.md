# Secure Task Manager

A simple Flask-based task management web application built for a cybersecurity academic project. This version contains intentionally added security vulnerabilities for educational testing purposes.

## Features

- User registration & login
- Session-based authentication
- Create, read, update, and delete (CRUD) tasks
- Task status tracking (Pending / Completed)
- Timestamps for task creation
- Modern, responsive UI

## Tech Stack

- Flask 3.0.0 (Python backend)
- SQLite database
- Jinja2 HTML templates
- Custom CSS (no external frameworks)

## Running the Application

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the app:
   ```bash
   python app.py
   ```

3. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000/
   ```

## Project Structure

```
secure-task-manager/
├── app.py                 # Main Flask application
├── schema.sql             # Database schema (users & tasks tables)
├── requirements.txt       # Python dependencies
├── README.md              # Project documentation
├── database.db            # SQLite database (auto-generated)
├── static/
│   └── css/
│       └── style.css      # Application styles
└── templates/
    ├── base.html          # Base layout with navigation & flash messages
    ├── login.html         # Login page
    ├── register.html      # Registration page
    ├── tasks.html         # Task list & creation form
    ├── task.html          # Task detail view
    └── edit_task.html     # Task edit form
```

## Important Notice

This application contains **intentional security vulnerabilities** for educational purposes:

- **SQL Injection** in the login route
- **Cross-Site Scripting (XSS)** in task detail templates
- **Insecure Direct Object Reference (IDOR)** in task access
- Hardcoded secret key and plaintext password storage

**Do not use this application in a production environment.**

