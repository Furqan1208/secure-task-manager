from flask import Flask, request, render_template, redirect, url_for, session, abort, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime
import os

# ---------------------------------------------------------------------------
# APP CONFIGURATION
# ---------------------------------------------------------------------------

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'database.db')
SCHEMA_PATH = os.path.join(BASE_DIR, 'schema.sql')

# ---------------------------------------------------------------------------
# DATABASE HELPERS
# ---------------------------------------------------------------------------

def get_db():
    """Return a new SQLite connection with Row factory for dict-like access."""
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db


def init_db():
    """Initialize the database by executing schema.sql."""
    with app.app_context():
        db = get_db()
        with open(SCHEMA_PATH, 'r') as f:
            db.executescript(f.read())
        db.commit()


@app.before_request
def setup():
    """Ensure the database is initialized before the first request."""
    if not hasattr(app, 'db_initialized'):
        init_db()
        app.db_initialized = True


# ---------------------------------------------------------------------------
# AUTHENTICATION HELPERS
# ---------------------------------------------------------------------------

def require_login():
    """Redirect to login if the user is not authenticated."""
    if 'user_id' not in session:
        return redirect(url_for('login'))


def get_current_user_id():
    """Return the currently logged-in user's ID, or None."""
    return session.get('user_id')


# ---------------------------------------------------------------------------
# TASK HELPERS (with ownership enforcement)
# ---------------------------------------------------------------------------

def get_user_tasks(user_id):
    """Fetch all tasks belonging to a specific user, newest first."""
    db = get_db()
    tasks = db.execute(
        "SELECT * FROM tasks WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,)
    ).fetchall()
    return tasks


def get_task_by_id(task_id, user_id):
    """Fetch a single task by ID only if it belongs to the given user."""
    db = get_db()
    task = db.execute(
        "SELECT * FROM tasks WHERE id = ? AND user_id = ?",
        (task_id, user_id)
    ).fetchone()
    return task


def delete_task_by_id(task_id, user_id):
    """Delete a task by ID only if it belongs to the given user."""
    db = get_db()
    cursor = db.execute(
        "DELETE FROM tasks WHERE id = ? AND user_id = ?",
        (task_id, user_id)
    )
    db.commit()
    return cursor.rowcount


def update_task(task_id, user_id, title, description, status):
    """Update task fields only if the task belongs to the given user."""
    db = get_db()
    cursor = db.execute(
        "UPDATE tasks SET title = ?, description = ?, status = ? WHERE id = ? AND user_id = ?",
        (title, description, status, task_id, user_id)
    )
    db.commit()
    return cursor.rowcount


def create_new_task(user_id, title, description, status):
    """Insert a new task into the database."""
    db = get_db()
    db.execute(
        "INSERT INTO tasks (user_id, title, description, status, created_at) VALUES (?, ?, ?, ?, ?)",
        (user_id, title, description, status, datetime.now().isoformat())
    )
    db.commit()


# ---------------------------------------------------------------------------
# AUTH ROUTES
# ---------------------------------------------------------------------------

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration with password hashing."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash("Username and password are required.", "error")
            return render_template('register.html')

        db = get_db()
        try:
            hashed_pw = generate_password_hash(password)
            db.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, hashed_pw)
            )
            db.commit()
            flash("Registration successful! Please log in.", "success")
        except sqlite3.IntegrityError:
            flash("Username already exists.", "error")
            return render_template('register.html')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login with parameterized queries and password hashing."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash("Username and password are required.", "error")
            return render_template('login.html')

        db = get_db()
        # SECURE: Parameterized query prevents SQL injection
        user = db.execute(
            "SELECT id, password FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            flash("Login successful!", "success")
            return redirect(url_for('tasks'))
        else:
            flash("Invalid credentials.", "error")
            return render_template('login.html')
    return render_template('login.html')


@app.route('/logout')
def logout():
    """Clear the user session and redirect to login."""
    session.pop('user_id', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))


# ---------------------------------------------------------------------------
# TASK ROUTES
# ---------------------------------------------------------------------------

@app.route('/')
def index():
    """Redirect root to tasks page or login."""
    if 'user_id' in session:
        return redirect(url_for('tasks'))
    return redirect(url_for('login'))


@app.route('/tasks')
def tasks():
    """Display the task list for the logged-in user."""
    redirect_resp = require_login()
    if redirect_resp:
        return redirect_resp

    user_id = get_current_user_id()
    tasks = get_user_tasks(user_id)
    return render_template('tasks.html', tasks=tasks)


@app.route('/task/<int:task_id>')
def view_task(task_id):
    """Display details for a single task. Enforces ownership."""
    redirect_resp = require_login()
    if redirect_resp:
        return redirect_resp

    user_id = get_current_user_id()
    task = get_task_by_id(task_id, user_id)
    if task is None:
        abort(404)

    # SECURE: Jinja2 auto-escaping is active; no |safe filter used
    return render_template('task.html', task=task)


@app.route('/create', methods=['POST'])
def create_task():
    """Handle creation of a new task."""
    redirect_resp = require_login()
    if redirect_resp:
        return redirect_resp

    user_id = get_current_user_id()
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    status = request.form.get('status', 'pending')

    if not title:
        flash("Task title is required.", "error")
        return redirect(url_for('tasks'))

    create_new_task(user_id, title, description, status)
    flash("Task created successfully!", "success")
    return redirect(url_for('tasks'))


@app.route('/task/<int:task_id>/edit', methods=['GET', 'POST'])
def edit_task(task_id):
    """Handle editing an existing task. Enforces ownership."""
    redirect_resp = require_login()
    if redirect_resp:
        return redirect_resp

    user_id = get_current_user_id()
    task = get_task_by_id(task_id, user_id)
    if task is None:
        abort(404)

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        status = request.form.get('status', 'pending')

        if not title:
            flash("Task title is required.", "error")
            return render_template('edit_task.html', task=task)

        updated = update_task(task_id, user_id, title, description, status)
        if updated == 0:
            abort(404)
        flash("Task updated successfully!", "success")
        return redirect(url_for('view_task', task_id=task_id))

    return render_template('edit_task.html', task=task)


@app.route('/task/<int:task_id>/delete', methods=['POST'])
def delete_task(task_id):
    """Handle deletion of a task. Enforces ownership."""
    redirect_resp = require_login()
    if redirect_resp:
        return redirect_resp

    user_id = get_current_user_id()
    deleted = delete_task_by_id(task_id, user_id)
    if deleted == 0:
        abort(404)

    flash("Task deleted successfully!", "success")
    return redirect(url_for('tasks'))


# ---------------------------------------------------------------------------
# MAIN ENTRY POINT
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    app.run(debug=True)

