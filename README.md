# Secure Task Manager - Vulnerable Version

WARNING: This version contains intentional security vulnerabilities for educational purposes only. Do not use it in production.

A Flask-based task manager built for security learning. It intentionally includes SQL Injection, IDOR, and Stored XSS vulnerabilities.

## Quick Start

```bash
pip install -r requirements.txt
python app.py
```

In another terminal:

```bash
python run_all_tests.py
```

App URL: http://localhost:5000

## Table of Contents

- [Overview](#overview)
- [Security Warning](#security-warning)
- [Vulnerabilities Summary](#vulnerabilities-summary)
- [Detailed Vulnerability Analysis](#detailed-vulnerability-analysis)
- [Setup](#setup)
- [Running the Application](#running-the-application)
- [Automated Security Testing](#automated-security-testing)
- [Manual Demonstration](#manual-demonstration)
- [Project Structure](#project-structure)
- [Fixing the Vulnerabilities](#fixing-the-vulnerabilities)
- [Technologies Used](#technologies-used)
- [Legal and Ethical Guidelines](#legal-and-ethical-guidelines)
- [Additional Resources](#additional-resources)
- [Support](#support)

## Overview

This project demonstrates common web security issues in a real app flow:

1. SQL Injection (CWE-89)
2. IDOR / Insecure Direct Object References (CWE-639)
3. Stored XSS (CWE-79)

Core app capabilities:

- User registration and login
- Task CRUD operations
- Multi-user behavior for authorization testing
- Script-based security test suite

## Security Warning

Do not:

- Deploy to public infrastructure
- Use with real user data
- Test outside authorized environments

Do:

- Run locally in an isolated lab VM/container
- Use for coursework and defensive learning
- Compare vulnerable and fixed branches

## Vulnerabilities Summary

| Vulnerability | CWE | Severity | Location |
| --- | --- | --- | --- |
| SQL Injection | CWE-89 | Critical | Login query in app.py |
| IDOR | CWE-639 | High | Task access/update/delete routes |
| Stored XSS | CWE-79 | High | task.html rendering with unsafe output |

## Detailed Vulnerability Analysis

### 1) SQL Injection (CWE-89)

Location: app.py login logic.

Vulnerable pattern:

```python
query = f"SELECT id FROM users WHERE username = '{username}' AND password = '{password}'"
user = db.execute(query).fetchone()
```

Why vulnerable:

- User-controlled input is concatenated into SQL.
- Attackers can alter query logic and bypass authentication.

Impact:

- Authentication bypass
- Unauthorized data access

### 2) IDOR (CWE-639)

Location: task read/edit/delete endpoints.

Vulnerable pattern:

```python
task = db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
```

Why vulnerable:

- Existence check is done, ownership check is not.
- Any logged-in user can target guessed IDs.

Impact:

- Read/modify/delete other users' tasks

### 3) Stored XSS (CWE-79)

Location: templates/task.html.

Vulnerable template pattern:

```html
<h2>{{ task.title | safe }}</h2>
<div class="task-description">{{ task.description | safe }}</div>
```

Why vulnerable:

- Untrusted content is rendered as executable HTML/JS.

Impact:

- Script execution in victim browser
- Session theft/phishing risk

## Setup

Prerequisites:

- Python 3.8+
- pip

Install:

```bash
# optional
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

## Running the Application

```bash
python app.py
```

Open http://localhost:5000

## Automated Security Testing

The repository includes:

- run_all_tests.py
- test_sql_injection.py
- test_idor.py
- test_xss.py

Run all tests:

```bash
python run_all_tests.py
```

Run individual tests:

```bash
python test_sql_injection.py
python test_idor.py
python test_xss.py
```

Expected result on vulnerable branch:

- SQL Injection: vulnerability detected
- IDOR: vulnerability detected
- XSS: vulnerability detected

Expected result on fixed branch:

- All tests pass with no vulnerabilities detected

Troubleshooting:

- Ensure app is running before tests.
- Run commands from the secure-task-manager directory.
- If DB state is noisy, stop app, delete database.db, restart app, rerun tests.

## Manual Demonstration

### SQL Injection

1. Go to /login.
2. Try username payload like: admin' OR '1'='1' --
3. Submit any password.
4. If login bypasses, vulnerability is confirmed.

### IDOR

1. Create User A and User B.
2. As User A, create a task.
3. As User B, access /task/<id-of-user-a-task>.
4. If visible/editable/deletable, vulnerability is confirmed.

### Stored XSS

1. Create a task with script-like payload in title or description.
2. Open task detail page.
3. If payload executes rather than displays safely, vulnerability is confirmed.

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

## Fixing the Vulnerabilities

Switch to fixed branch:

```bash
git checkout fixed
```

Typical fixes:

- SQL Injection: parameterized queries
- IDOR: ownership checks (`AND user_id = ?`)
- XSS: safe output rendering (remove unsafe template usage)

## Technologies Used

- Flask
- SQLite3
- Jinja2 templates
- Python 3.8+

## Legal and Ethical Guidelines

- Use only in authorized environments.
- Do not test systems without permission.
- This code is intentionally vulnerable for education.

## Additional Resources

- OWASP Top 10
- PortSwigger Web Security Academy
- OWASP SQL Injection, IDOR, and XSS guidance

## Support

If results look inconsistent:

1. Confirm branch and current code state.
2. Confirm app is running on localhost:5000.
3. Reset database.db and rerun tests.
4. Compare against fixed branch behavior.
