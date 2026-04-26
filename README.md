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
