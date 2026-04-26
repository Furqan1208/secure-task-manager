# Secure Task Manager - Vulnerable Version

**⚠️ WARNING: This version contains intentional security vulnerabilities for educational purposes ONLY.**

A Flask-based task management application with three deliberately placed security vulnerabilities to demonstrate and teach common web application security flaws.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Start the application
python app.py

# In another terminal, run tests
python run_all_tests.py
```

The application will be available at `http://localhost:5000`

---

## Table of Contents

- [Overview](#overview)
- [Security Warning](#security-warning)
- [Vulnerabilities Summary](#vulnerabilities-summary)
- [Detailed Vulnerability Analysis](#detailed-vulnerability-analysis)
- [Setup Instructions](#setup-instructions)
- [Running the Application](#running-the-application)
- [Automated Security Testing](#automated-security-testing)
- [Manual Vulnerability Demonstration](#manual-vulnerability-demonstration)
- [Project Structure](#project-structure)
- [Fixing the Vulnerabilities](#fixing-the-vulnerabilities)
- [Technologies](#technologies)
- [Legal & Ethical Guidelines](#legal--ethical-guidelines)

## Overview

This educational application demonstrates three OWASP Top 10 vulnerabilities in a working web application:

1. **SQL Injection** - Unsanitized user input in database queries
2. **IDOR (Insecure Direct Object References)** - Missing authorization checks
3. **XSS (Stored Cross-Site Scripting)** - Unsafe template rendering

### Features

- User registration and authentication
- Create, read, update, and delete (CRUD) tasks
- Multi-user task management
- Automated security test suite

## Security Warning
### ❌ DO NOT

- Deploy in production
- Use with real user data
- Expose to the internet
- Use on shared systems

### ✅ DO

- Use only in isolated development environments
- Use for educational purposes in authorized settings
- Use for authorized penetration testing
- Study the vulnerabilities and understand fixes

---

## Vulnerabilities Summary

| # | Vulnerability | CWE | Severity | Location |
|---|---|---|---|---|
---

## Detailed Vulnerability Analysis

### 1. SQL Injection (CWE-89)

**Location:** `app.py` - Login route

**Vulnerable Code:**
```python
query = f"SELECT id FROM users WHERE username = '{username}' AND password = '{password}'"
cursor = db.execute(query)
user = cursor.fetchone()
```

**The Problem:**
- User input directly concatenated into SQL query
- No input validation or parameterization
- Attackers can modify query logic

**Impact:**
- Authentication bypass without credentials
- Unauthorized database access
- Potential data theft or modification
- Complete application compromise

**Example Attack:**
```
Username: admin' OR '1'='1' --
**Location:** `app.py` - Task routes (`/task/<id>`, `/task/<id>/edit`, `/task/<id>/delete`)

**Vulnerable Code:**
```python
@app.route('/task/<int:task_id>')
def view_task(task_id):
    task = get_task_by_id(task_id)  # No ownership check!
    if task is None:
        abort(404)
    return render_template('task.html', task=task)
```

**The Problem:**
- No authorization verification
- Only checks if task exists, not if user owns it
- Task IDs are sequential and guessable

**Impact:**
- Unauthorized viewing of other users' tasks
- Modification of other users' tasks
- Deletion of other users' tasks
- Privacy breach and data tampering

**Example Attack:**
```
1. Create account as User A
2. Create a task (ID = 1)
3. Log in as User B
4. VisiStored XSS - Cross-Site Scripting (CWE-79)

**Location:** Task creation and display

**Vulnerable Template Code:**
```html
<!-- templates/task.html -->
<h2>{{ task.title | safe }}</h2>
<div class="task-description">
    {{ task.description | safe }}
</div>
```

**The Problem:**
- User input stored without sanitization
- `| safe` filter renders HTML/JavaScript unescaped
- Malicious scripts execute in user's browser

**Impact:**
- Session hijacking (steal authentication cookies)
- Redirect to malicious sites
- Phishing attacks
- Defacement of application

**Example Attack:**
```
Task Title: <img src=x onerror="alert('XSS Attack!')">
Task Description: <script>/* malicious code */</script>
``` }}
</div>
```

What is wrong:

---

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip package manager
- 50MB free disk space
- Isolated environment (recommended: VM or container)

### Installation Steps

1. **Navigate to project directory:**
   ```bash
   cd secure-task-manager
   ```

2. **Create virtual environment:**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Mac/Linux
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the application:**
   ```bash
   python app.py
   ```

5. **Access the application:**
   ```
   http://localhost:5000
   ```

**Note:** The database (`database.db`) is automatically 

Requirements:

```text
Flask==2.3.0
```

### 5. Initialize Database

The database is auto-created on first run.

## Running the Application

### Start the Vulnerable Server

```bash
---

## Running the Application

### Start the Server

```bash
python app.py
```

Expected output:
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

### Access the Web Interface

1. Open browser to `http://localhost:5000`
2. Register a new account
3. Create, edit, view, and delete tasks
4. Log out and try to access other users' tasks by URL

---
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
    - Start server first withscripts to automatically detect and verify all three vulnerabilities.

### Test Scripts

| Script | Purpose |
|--------|---------|
| `run_all_tests.py` | Runs all three test suites sequentially |
| `test_sql_injection.py` | Tests SQL Injection vulnerability |
| `test_idor.py` | Tests IDOR vulnerability |
| `test_xss.py` | Tests Stored XSS vulnerability |

### Running Tests

#### 1. Run All Tests
```bash
python run_all_tests.py
```

#### 2. Run Individual Tests
```bash
# Test SQL Injection
python test_sql_injection.py

# Test IDOR
python test_idor.py

# Test XSS
python test_xss.py
```

### Expected Test Results

**On `main` branch (vulnerable version):**
```
RUNNING: SQL Injection Tests
[FAIL] SQL INJECTION VULNERABILITIES DETECTED ✓ (Expected)

RUNNING: IDOR Tests
[FAIL] IDOR VULNERABILITIES DETECTED ✓ (Expected)

RUNNING: XSS Tests
[FAIL] XSS VULNERABILITIES DETECTED ✓ (Expected)

TOTAL: 0 passed, 3 failed
```

**On `fixed` branch (secure version):**
```
RUNNING: SQL Injection Tests
[PASS] No SQL injection vulnerability detected ✓

RUNNING: IDOR Tests
[PASS] No IDOR vulnerabilities detected ✓

RUNNING: XSS Tests
[PASS] No XSS vulnerability detected ✓

TOTAL: 3 passed, 0 failed
```

### Test Execution Requirements
---

## Project Structure

```
secure-task-manager/
│
├── app.py                          # Main Flask application (VULNERABLE)
├── schema.sql                      # Database schema
├── requirements.txt                # Python dependencies
├── database.db                     # SQLite database (auto-created)
│
├── run_all_tests.py               # Master test runner
├── test_sql_injection.py           # SQL Injection test suite
├── test_idor.py                   # IDOR test suite
├── test_xss.py                    # XSS test suite
│
├── static/
│   └── css/
│       └── style.css              # Application styling
│
├── templates/
│   ├── base.html                  # Base template (layout)
│   ├── login.html                 # Login page
│   ├── register.html              # Registration page
│   ├── tasks.html                 # Task list view
│   ├── task.html                  # Task detail view (vulnerable)
│   └── edit_task.html             # Task edit form
│
└── README.md                       # This file
```

---

## Fixing the Vulnerabilities

The secure version with all fixes applied is available on the `fixed` branch:

```bash
git checkout fixed
```

### Fix Summary

| Vulnerability | Fix Applied |
|---|---|
| **SQL Injection** | Parameterized queries using `?` placeholders |
| **IDOR** | Authorization checks: `WHERE id = ? AND user_id = ?` |
| **XSS** | Remove `\| safe` filters; Jinja2 auto-escapes by default |

### Key Security Improvements

1. **SQL Injection Fix:**
   ```python
   # Before (VULNERABLE)
   query = f"SELECT id FROM users WHERE username = '{username}' AND password = '{password}'"
   
   # After (FIXED)
   cursor = db.execute("SELECT id FROM users WHERE username = ? AND password = ?", 
                       (username, password))
   ```

2. **IDOR Fix:**
   ```python
   # Before (VULNERABLE)
   task = db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
   
   # After (FIXED)
   task = db.execute("SELECT * FROM tasks WHERE id = ? AND user_id = ?", 
                     (task_id, current_user_id)).fetchone()
   ```

3. **XSS Fix:**
   ```html
   <!-- Before (VULNERABLE) -->
   <h2>{{ task.title | safe }}</h2>
   
   <!-- After (FIXED) -->
   <h2>{{ task.title }}</h2>  <!-- Auto-escaped -->
   ```

---

## Technologies

- **Backend:** Flask 2.3.0 (Python web framework)
- **Database:** SQLite3 (embedded SQL database)
- **Frontend:** HTML5, CSS3, Jinja2 templating
- **Language:** Python 3.8+
- **Testing:** requests (HTTP client library)

---

## Legal & Ethical Guidelines

### ⚖️ Legal Disclaimer

This software is provided **for educational purposes only**. All vulnerabilities are **intentional**.

- The authors assume no liability for misuse or damage
- Users are responsible for legal compliance
- Unauthorized testing on systems you don't own is illegal

### ✅ Ethical Use

- **Do:** Use this in authorized lab environments
- **Do:** Follow your institution's policies
- **Do:** Get written permission before testing any system
- **Don't:** Test on production systems
- **Don't:** Test on systems you don't own or have permission for
- **Don't:** Use findings for malicious purposes

### 📚 Educational Purpose

This project is designed for:
- Computer science students learning web security
- Instructors demonstrating security vulnerabilities
- Security professionals practicing attack techniques
- Organizations conducting authorized security training

---

## Additional Resources

### Learning Materials
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [PortSwigger Web Security Academy](https://portswigger.net/web-security)
- [OWASP SQL Injection](https://owasp.org/www-community/attacks/SQL_Injection)
- [OWASP IDOR](https://owasp.org/www-community/attacks/Insecure_Direct_Object_References)
- [OWASP XSS](https://owasp.org/www-community/attacks/xss/)

### Prevention Cheat Sheets
- [SQL Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
- [XSS Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [Authorization Testing](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/05-Authorization_Testing/README)

---

## Support

For issues or questions about this educational project, please refer to the course materials or instructor.

---

**Last Updated:** April 2026  
**Course:** Secure Software Design and Development  
**Status:** Educational Version (Vulnerable - For Learning Only)ses. The authors assume no liability for misuse or damage caused by this software. Users are responsible for complying with applicable laws and regulations.

## License

This project is for educational purposes as part of Secure Software Design and Development coursework.

## Additional Learning Resources

- OWASP Top 10
- PortSwigger Web Security Academy
- SQL Injection Prevention Cheat Sheet
- XSS Prevention Cheat Sheet
- IDOR Prevention Guidance

Reminder: Switch to `fixed` branch for the secure version of this application.
