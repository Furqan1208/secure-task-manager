# Secure Task Manager - Vulnerable Version (Educational Purpose Only)

**WARNING: This version contains intentional security vulnerabilities for educational purposes. DO NOT use this in production or any real-world environment.**

A task management web application with intentionally placed security vulnerabilities to demonstrate common web application flaws including SQL Injection, IDOR (Insecure Direct Object References), and XSS (Cross-Site Scripting).

## Table of Contents

- [Overview](#overview)
- [Security Warning](#security-warning)
- [Intentional Vulnerabilities](#intentional-vulnerabilities)
- [Vulnerability Details](#vulnerability-details)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [Demonstrating Vulnerabilities](#demonstrating-vulnerabilities)
- [Automated Security Testing](#automated-security-testing)
- [Project Structure](#project-structure)
- [Technologies Used](#technologies-used)
- [Educational Purpose](#educational-purpose)
- [Fixing the Vulnerabilities](#fixing-the-vulnerabilities)

## Overview

This is a vulnerable task management web application designed for educational and testing purposes. It allows users to:

- Register new accounts
- Login with authentication
- Create, read, update, and delete tasks

However, it contains three critical security vulnerabilities that can be exploited:

1. SQL Injection in the login functionality
2. IDOR (Insecure Direct Object References) in task management
3. XSS (Cross-Site Scripting) in task creation and display

## Security Warning

**THIS IS A DELIBERATELY VULNERABLE APPLICATION**

- DO NOT deploy this on any public server
- DO NOT use this with real user data
- DO NOT use this in production environments
- ONLY use this for educational purposes in isolated environments
- ONLY use this to learn about security vulnerabilities
- ONLY use this to practice penetration testing in authorized lab settings

## Intentional Vulnerabilities

This application contains three distinct security vulnerabilities as required for the Secure Software Design and Development coursework:

| # | Vulnerability | CWE | Location | Severity |
| --- | --- | --- | --- | --- |
| 1 | SQL Injection | CWE-89 | Login form (`/login`) | Critical |
| 2 | IDOR | CWE-639 | Task URLs (`/task/<id>`) | High |
| 3 | XSS (Stored) | CWE-79 | Task creation/display | High |

## Vulnerability Details

### 1. SQL Injection (CWE-89)

Location: Login route in `app.py`

Vulnerable code:

```python
# VULNERABLE - String concatenation in SQL query
query = "SELECT id FROM users WHERE username = '" + username + "' AND password = '" + password + "'"
cursor.execute(query)
```

What is wrong:

- User input is directly concatenated into SQL query
- No parameterization or sanitization
- Attacker can modify query structure

Impact:

- Authentication bypass
- Database data theft
- Potential database modification
- Complete system compromise

### 2. IDOR - Insecure Direct Object References (CWE-639)

Location: Task routes in `app.py`

Vulnerable code:

```python
# VULNERABLE - No ownership verification
task = db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
# No check if task belongs to current user
```

What is wrong:

- No authorization checks for task access
- Users can access any task by guessing IDs
- No ownership verification

Impact:

- Unauthorized access to other users' tasks
- Viewing private task data
- Modifying other users' tasks
- Deleting other users' tasks

### 3. XSS - Cross-Site Scripting (CWE-79)

Location: Task creation and display in `app.py` and templates

Vulnerable code:

```python
# VULNERABLE - No HTML escaping
title = request.form['title']
description = request.form['description']
```

Template pattern:

```html
<!-- VULNERABLE - Unsafe rendering -->
<h2>{{ task.title | safe }}</h2>
<div class="task-description">
    {{ task.description | safe }}
</div>
```

What is wrong:

- User input stored without sanitization
- Template allows unsafe rendering
- Script content can execute in browser context

Impact:

- Session hijacking risk
- Cookie theft risk
- Phishing and defacement risk

## Prerequisites

Before running this vulnerable application, ensure you have:

- Python 3.8 or higher
- `pip` (Python package manager)
- Git (optional)
- Isolated environment (VM or container recommended)

## Installation

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd secure-task-manager
```

### 2. Stay on Main Branch (Vulnerable Version)

```bash
git checkout main
```

### 3. Create Virtual Environment (Recommended for isolation)

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
```

### 5. Initialize Database

The database is auto-created on first run.

## Running the Application

### Start the Vulnerable Server

```bash
python app.py
```

Note: Debug mode may be enabled for vulnerability demonstration.

### Access the Application

```text
http://localhost:5000
```

## Demonstrating Vulnerabilities

### Demo 1: SQL Injection (Authentication Bypass)

Goal: Show that unsafe query construction can bypass login checks.

High-level steps:

1. Open the login page.
2. Enter a crafted username payload that alters SQL logic.
3. Submit any password.
4. Observe whether authentication is bypassed.

Expected result:

- Login may succeed without valid credentials.
- Demonstrates why parameterized queries are required.

### Demo 2: IDOR (Access Other Users' Tasks)

Goal: Show missing ownership checks on task resources.

High-level steps:

1. Create two users.
2. Create a task as User A.
3. Log in as User B.
4. Attempt to access User A task URL by task ID.

Expected result:

- User B may view or alter User A data.
- Demonstrates broken authorization.

### Demo 3: XSS (Stored Cross-Site Scripting)

Goal: Show unsafe rendering of user-supplied content.

High-level steps:

1. Create a task using script-like input in title or description.
2. Save and view the task.
3. Observe whether browser executes injected content.

Expected result:

- Browser executes content instead of displaying harmless text.
- Demonstrates need for escaping and safe templating.

## Automated Security Testing

This project includes Python test scripts to validate the three intentional vulnerabilities.

### Included Test Scripts

- `run_all_tests.py` - runs all vulnerability tests in sequence
- `test_sql_injection.py` - tests SQL Injection behaviors
- `test_idor.py` - tests IDOR behaviors
- `test_xss.py` - tests stored XSS behaviors

### Before Running Tests

1. Start the app in one terminal:

```bash
python app.py
```

2. In a second terminal, run tests from the project folder:

```bash
cd secure-task-manager
```

### Run Full Test Suite

```bash
python run_all_tests.py
```

### Run Individual Test Suites

```bash
python test_sql_injection.py
python test_idor.py
python test_xss.py
```

### How to Read Results

For `main` (vulnerable version):

- SQL Injection should be reported as vulnerable
- IDOR should be reported as vulnerable
- XSS should be reported as vulnerable
- Overall suite should indicate vulnerabilities detected

For `fixed` branch:

- All three test suites should pass with no vulnerabilities detected

### Common Testing Issues

- App not running:
    - Start server first with `python app.py`
- Wrong folder:
    - Run tests inside `secure-task-manager`, not parent directory
- Database state confusion from repeated runs:
    - Stop app, delete `database.db`, restart app, rerun tests
- Port conflict on 5000:
    - Change app port and update `BASE_URL` in test files to match

## Project Structure

```text
secure-task-manager/
├── app.py                 # Main Flask application (VULNERABLE)
├── schema.sql             # Database schema definition
├── requirements.txt       # Python dependencies
├── database.db            # SQLite database (auto-created)
├── static/
│   └── css/
│       └── style.css      # Application styling
├── templates/
│   ├── base.html          # Base template
│   ├── login.html         # Login page
│   ├── register.html      # Registration page
│   ├── tasks.html         # Task listing
│   ├── task.html          # Task view
│   └── edit_task.html     # Edit form
└── README.md              # This file
```

## Technologies Used

- Backend Framework: Flask 2.3.0
- Database: SQLite3
- Frontend: HTML5, CSS3, Jinja2 templating
- Language: Python 3.8+

## Educational Purpose

This vulnerable application is designed to help students understand:

- How SQL Injection occurs with unsanitized SQL construction
- Why IDOR appears when authorization checks are missing
- How stored XSS executes when content is rendered unsafely
- Why secure coding practices must be applied end-to-end

Who should use this:

- Students learning web security
- Instructors demonstrating security flaws
- Developers studying secure design principles

Ethical use guidelines:

- Use only in isolated local environments
- Test only on systems you own or are authorized to assess
- Follow applicable laws and institutional policies

## Fixing the Vulnerabilities

The fixed version of this application is available on the `fixed` branch:

```bash
git checkout fixed
```

Summary of fixes applied in the secure version:

| Vulnerability | Fix Method |
| --- | --- |
| SQL Injection | Parameterized queries and validation |
| IDOR | Ownership checks with `AND user_id = ?` |
| XSS | HTML escaping and safe template rendering |

## Troubleshooting

### Database Issues

Delete `database.db` and restart the app. It will be recreated.

### Debug Mode Issues

Debug settings are defined in `app.py`.

### Port Conflicts

Change port in `app.py`:

```python
app.run(debug=True, port=5001)
```

## Legal Disclaimer

This software is provided for educational purposes only.

The vulnerabilities in this application are intentional and for learning purposes. The authors assume no liability for misuse or damage caused by this software. Users are responsible for complying with applicable laws and regulations.

## License

This project is for educational purposes as part of Secure Software Design and Development coursework.

## Additional Learning Resources

- OWASP Top 10
- PortSwigger Web Security Academy
- SQL Injection Prevention Cheat Sheet
- XSS Prevention Cheat Sheet
- IDOR Prevention Guidance

Reminder: Switch to `fixed` branch for the secure version of this application.
