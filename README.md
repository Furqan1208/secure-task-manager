# Secure Task Manager - Fixed Version

A secure task management web application demonstrating proper security implementations including protection against SQL Injection, IDOR (Insecure Direct Object References), and XSS (Cross-Site Scripting) vulnerabilities.

## Table of Contents

- [Overview](#overview)
- [Security Features](#security-features)
- [Fixed Vulnerabilities](#fixed-vulnerabilities)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [Testing Security Fixes](#testing-security-fixes)
- [Project Structure](#project-structure)
- [Technologies Used](#technologies-used)
- [Security Implementation Details](#security-implementation-details)
- [Comparison with Vulnerable Version](#comparison-with-vulnerable-version)

## Overview

This is a secure task management web application that allows users to:

- Register new accounts with secure password hashing
- Login with proper authentication
- Create, read, update, and delete their own tasks
- View tasks organized by creation date

The application implements multiple security layers to protect against common web vulnerabilities.

## Security Features

### Implemented Security Measures

1. **SQL Injection Prevention**
   - Parameterized queries throughout all database operations
   - No string concatenation or formatting in SQL queries

2. **IDOR (Insecure Direct Object References) Prevention**
   - Ownership verification on every task operation
   - Users can only access their own tasks
   - Server-side authorization checks for all CRUD operations

3. **XSS (Cross-Site Scripting) Prevention**
   - HTML escaping at input time using `html.escape()`
   - Jinja2 auto-escaping enabled by default
   - No `|safe` filters in templates
   - Content-Type headers properly set

4. **Additional Security Features**
   - Password hashing with Werkzeug (pbkdf2:sha256)
   - Session-based authentication
   - Username validation (alphanumeric + underscore only)
   - Debug mode disabled in production
   - Secure secret key management

## Fixed Vulnerabilities

The following vulnerabilities present in the vulnerable version have been fixed:

| Vulnerability | Description | Impact | Fix Implementation |
| --- | --- | --- | --- |
| SQL Injection | Malicious SQL code injected through login form | Database compromise, data theft | Parameterized queries with `?` placeholders |
| IDOR | Users accessing/modifying other users' tasks | Unauthorized data access/modification | Ownership verification with `AND user_id = ?` |
| XSS | Malicious scripts injected via task titles/descriptions | Session hijacking, data theft | HTML escaping + Jinja2 auto-escaping |

## Prerequisites

Before running this application, ensure you have:

- Python 3.8 or higher
- `pip` (Python package manager)
- Git (optional, for cloning)

## Installation

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd secure-task-manager
```

### 2. Switch to Fixed Version Branch

```bash
git checkout fixed
```

### 3. Create Virtual Environment (Recommended)

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

Mac/Linux:

```bash
python -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

Requirements:

```text
Flask==2.3.0
werkzeug==2.3.0
```

### 5. Initialize Database

The database will be automatically created when you first run the application. The `schema.sql` file defines:

- `users` table: Stores user credentials with hashed passwords
- `tasks` table: Stores tasks linked to users with ownership tracking

## Running the Application

### Start the Flask Server

```bash
python app.py
```

### Access the Application

Open your web browser and navigate to:

```text
http://localhost:5000
```

### Default Actions

- Register - Create a new account
- Username: letters, numbers, underscores only
- Password: any characters (will be hashed)
- Login - Access your account
- Uses secure password verification
- Create Tasks - Add new tasks with title, description, and status
- Manage Tasks - View, edit, or delete your own tasks only

## Testing Security Fixes

### Test 1: SQL Injection Prevention

Attempt malicious login:

```text
Username: admin' OR '1'='1
Password: anything
```

Expected Result:

- Login fails with "Invalid credentials"
- Database remains secure
- No unauthorized access granted

### Test 2: IDOR Prevention

Scenario: User A tries to access User B's task

1. Create two accounts: `user1` and `user2`
2. As `user1`, create a task (for example, task ID = 1)
3. Logout and login as `user2`
4. Attempt to access: `http://localhost:5000/task/1`

Expected Result:

- 404 Not Found or redirect to tasks page
- Flash message: "Task not found or you don't have permission"

### Test 3: XSS Prevention

Attempt XSS injection when creating task:

```text
Title: <script>alert('XSS')</script>
Description: <img src=x onerror=alert('Hacked')>
```

Expected Result:

- Script tags are escaped and displayed as text
- No JavaScript execution in browser
- Task shows: `&lt;script&gt;alert('XSS')&lt;/script&gt;`

## Project Structure

```text
secure-task-manager/
├── app.py                 # Main Flask application (FIXED version)
├── schema.sql             # Database schema definition
├── requirements.txt       # Python dependencies
├── database.db            # SQLite database (auto-created)
├── static/
│   └── css/
│       └── style.css      # Application styling
├── templates/
│   ├── base.html         # Base template with navigation
│   ├── login.html        # Login page
│   ├── register.html     # Registration page
│   ├── tasks.html        # Task listing and creation
│   ├── task.html         # Individual task view
│   └── edit_task.html    # Task editing form
└── README.md             # This file
```

## Technologies Used

- Backend Framework: Flask 2.3.0
- Database: SQLite3
- Security Libraries:
  - Werkzeug (password hashing)
  - HTML (HTML escaping)
  - `re` (input validation)
- Frontend: HTML5, CSS3, Jinja2 templating
- Language: Python 3.8+

## Security Implementation Details

### 1. SQL Injection Prevention

Vulnerable Code (Fixed):

```python
# BAD - Vulnerable to SQL injection
query = f"SELECT * FROM users WHERE username = '{username}'"
```

Fixed Code:

```python
# GOOD - Uses parameterized queries
query = "SELECT * FROM users WHERE username = ?"
cursor.execute(query, (username,))
```

### 2. IDOR Prevention

Vulnerable Code (Fixed):

```python
# BAD - No ownership verification
task = db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
```

Fixed Code:

```python
# GOOD - Verifies ownership
task = db.execute(
    "SELECT * FROM tasks WHERE id = ? AND user_id = ?",
    (task_id, user_id)
)
```

### 3. XSS Prevention

Vulnerable Code (Fixed):

```python
# BAD - No escaping
task.title = request.form['title']
```

Fixed Code:

```python
# GOOD - HTML escaping at input
import html
task.title = html.escape(request.form['title'])
```

## Comparison with Vulnerable Version

| Aspect | Vulnerable Version (main branch) | Fixed Version (fixed branch) |
| --- | --- | --- |
| SQL Queries | String concatenation | Parameterized queries |
| Task Access | No ownership checks | Ownership verification on all operations |
| Input Handling | No escaping | HTML escaping on all user input |
| Password Storage | Plain text (in vulnerable version) | Hashed with Werkzeug |
| Debug Mode | Enabled | Disabled |
| XSS Protection | None (vulnerable templates) | Jinja2 auto-escaping + input escaping |

## Security Best Practices Implemented

- Principle of Least Privilege - Users only access their own data
- Defense in Depth - Multiple security layers (input validation, output escaping, authorization)
- Secure Defaults - Auto-escaping enabled, debug disabled
- Input Validation - Username format validation
- Output Encoding - HTML escaping for all user-generated content
- Authentication - Session-based with proper secret key
- Password Security - Hashed passwords, no plain text storage

## Troubleshooting

### Database Issues

If you encounter database errors, delete `database.db` and restart the application - it will be recreated automatically.

### Port Already in Use

```bash
# Change port in app.py
app.run(debug=False, port=5001)
```

### Template Errors

Ensure all template files are in the `templates/` directory with correct names.

## License

This project is for educational purposes as part of Secure Software Design and Development coursework.

## Acknowledgments

- Flask Security Documentation
- OWASP Top 10 Web Application Security Risks
- Secure Software Development Lifecycle (SSDL) principles

## Support

For issues or questions regarding this fixed version:

- Check the troubleshooting section above
- Verify you're on the fixed branch
- Ensure all dependencies are installed correctly

Note: This is the secure version of the application. The vulnerable version is available on the main branch for educational purposes to demonstrate common web vulnerabilities and their fixes.

