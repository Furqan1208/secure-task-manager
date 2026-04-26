# Secure Task Manager - Fixed Version

A secure task management web application demonstrating protection against SQL Injection, IDOR (Insecure Direct Object References), and XSS (Cross-Site Scripting).

## Table of Contents

- [Overview](#overview)
- [Security Features](#security-features)
- [Fixed Vulnerabilities](#fixed-vulnerabilities)
- [Setup](#setup)
- [Running the Application](#running-the-application)
- [Testing Security Fixes](#testing-security-fixes)
- [Security Implementation Details](#security-implementation-details)
- [Security Best Practices Implemented](#security-best-practices-implemented)
- [Comparison with Vulnerable Version](#comparison-with-vulnerable-version)
- [Project Structure](#project-structure)
- [Technologies Used](#technologies-used)
- [Troubleshooting](#troubleshooting)
- [License](#license)
- [Acknowledgments](#acknowledgments)
- [Support](#support)

## Overview

This secure version of the application allows users to:

- Register new accounts
- Login with proper authentication
- Create, read, update, and delete only their own tasks
- View tasks in an organized task list

It applies multiple security controls to reduce common web application risks.

## Security Features

### Implemented Security Measures

1. SQL Injection Prevention
- Parameterized queries across database operations
- No direct SQL string concatenation with user input

2. IDOR Prevention
- Ownership checks on task read/update/delete operations
- Access limited to resources owned by the authenticated user

3. XSS Prevention
- Input escaping and safe rendering strategy
- No unsafe template rendering pattern in secure templates

4. Additional Security Controls
- Password hashing with Werkzeug
- Session-based authentication
- Username validation
- Safer runtime configuration (debug disabled for secure mode)

## Fixed Vulnerabilities

The following vulnerabilities from the vulnerable version are addressed:

| Vulnerability | Description | Impact | Fix Implementation |
| --- | --- | --- | --- |
| SQL Injection | Malicious SQL payload through login input | Unauthorized access, data risk | Parameterized queries with placeholders |
| IDOR | Accessing or modifying other users' tasks | Broken authorization | Ownership check using `user_id` |
| XSS | Injected scripts in task fields | Browser-side script execution | Escaping + safe template rendering |

## Setup

### Prerequisites

- Python 3.8 or higher
- `pip`
- Git (optional)

### Installation

1. Clone the repository

```bash
git clone <your-repository-url>
cd secure-task-manager
```

2. Checkout fixed branch

```bash
git checkout fixed
```

3. Create and activate a virtual environment (recommended)

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

4. Install dependencies

```bash
pip install -r requirements.txt
```

The database is created automatically on first run.

## Running the Application

Start the server:

```bash
python app.py
```

Open:

```text
http://localhost:5000
```

## Testing Security Fixes

Run from the project root while the app is running.

### Run full suite

```bash
python run_all_tests.py
```

### Run individual suites

```bash
python test_sql_injection.py
python test_idor.py
python test_xss.py
```

### Expected result on fixed version

- SQL Injection tests should pass
- IDOR tests should pass
- XSS tests should pass

## Security Implementation Details

### SQL Injection Prevention

```python
# Preferred pattern: parameterized query
query = "SELECT * FROM users WHERE username = ?"
cursor.execute(query, (username,))
```

### IDOR Prevention

```python
# Preferred pattern: enforce ownership in query
task = db.execute(
    "SELECT * FROM tasks WHERE id = ? AND user_id = ?",
    (task_id, user_id)
)
```

### XSS Prevention

```python
# Preferred pattern: escape untrusted input before storage or output
import html
safe_title = html.escape(request.form['title'])
```

## Security Best Practices Implemented

- Principle of least privilege for task access
- Defense in depth across validation, authorization, and rendering
- Secure defaults for runtime behavior
- Output encoding for user-controlled content
- Session-based authentication and password hashing

## Comparison with Vulnerable Version

| Aspect | Vulnerable Version (main branch) | Fixed Version (fixed branch) |
| --- | --- | --- |
| SQL Handling | Dynamic query construction | Parameterized queries |
| Authorization | Missing ownership checks | Ownership enforced per operation |
| Rendering | Unsafe output possible | Escaping and safe rendering |

## Project Structure

```text
secure-task-manager/
├── app.py
├── schema.sql
├── requirements.txt
├── run_all_tests.py
├── test_sql_injection.py
├── test_idor.py
├── test_xss.py
├── static/
│   └── css/
│       └── style.css
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── tasks.html
│   ├── task.html
│   └── edit_task.html
└── README.md
```

## Technologies Used

- Flask
- SQLite3
- Jinja2 templates
- Werkzeug
- Python 3.8+

## Troubleshooting

### App does not start

- Confirm dependencies are installed
- Check if another process is using port 5000

### Database issues

- Stop the app
- Delete `database.db`
- Restart the app to recreate schema

### Test failures

- Ensure app is running on `http://localhost:5000`
- Run tests from the `secure-task-manager` directory

## License

This project is for educational purposes as part of Secure Software Design and Development coursework.

## Acknowledgments

- Flask documentation
- OWASP Top 10
- Secure Software Development Lifecycle (SSDL) guidance

## Support

For issues or questions:

- Check Troubleshooting first
- Confirm you are on the `fixed` branch
- Confirm dependencies are installed and environment is active

The vulnerable reference version remains available on `main` for learning and comparison.

