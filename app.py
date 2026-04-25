from flask import Flask, request, render_template, redirect, url_for, session, abort, flash
import sqlite3
from datetime import datetime
import os

# ---------------------------------------------------------------------------
# APP CONFIGURATION
# ---------------------------------------------------------------------------

app = Flask(__name__)
app.secret_key = 'insecure-secret-key-for-demo'

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
# TASK HELPERS
# ---------------------------------------------------------------------------

def get_user_tasks(user_id):
    """Fetch all tasks belonging to a specific user, newest first."""
    db = get_db()
    tasks = db.execute(
        "SELECT * FROM tasks WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,)
    ).fetchall()
    return tasks


def get_task_by_id(task_id):
    """Fetch a single task by its ID. No ownership check — used for detail view."""
    db = get_db()
    task = db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    return task


def delete_task_by_id(task_id):
    """Delete a task by ID."""
    db = get_db()
    db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    db.commit()


def update_task(task_id, title, description, status):
    """Update task fields."""
    db = get_db()
    db.execute(
        "UPDATE tasks SET title = ?, description = ?, status = ? WHERE id = ?",
        (title, description, status, task_id)
    )
    db.commit()


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
    """Handle user registration."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        try:
            db.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                       (username, password))
            db.commit()
            flash("Registration successful! Please log in.", "success")
        except sqlite3.IntegrityError:
            flash("Username already exists.", "error")
            return render_template('register.html')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()

        # VULNERABILITY: SQL Injection — intentionally using string formatting
        # to allow manipulation of the query for educational testing.
        query = f"SELECT id FROM users WHERE username = '{username}' AND password = '{password}'"
        cursor = db.execute(query)
        user = cursor.fetchone()

        if user:
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
    """Display details for a single task."""
    redirect_resp = require_login()
    if redirect_resp:
        return redirect_resp

    # VULNERABILITY: IDOR — No ownership verification.
    # Any authenticated user can view any task by ID.
    task = get_task_by_id(task_id)
    if task is None:
        abort(404)

    # VULNERABILITY: XSS — The template uses |safe filter on task fields,
    # allowing script injection to execute in the browser.
    return render_template('task.html', task=task)


@app.route('/create', methods=['POST'])
def create_task():
    """Handle creation of a new task."""
    redirect_resp = require_login()
    if redirect_resp:
        return redirect_resp

    user_id = get_current_user_id()
    title = request.form['title']
    description = request.form.get('description', '')
    status = request.form.get('status', 'pending')

    create_new_task(user_id, title, description, status)
    flash("Task created successfully!", "success")
    return redirect(url_for('tasks'))


@app.route('/task/<int:task_id>/edit', methods=['GET', 'POST'])
def edit_task(task_id):
    """Handle editing an existing task."""
    redirect_resp = require_login()
    if redirect_resp:
        return redirect_resp

    task = get_task_by_id(task_id)
    if task is None:
        abort(404)

    if request.method == 'POST':
        title = request.form['title']
        description = request.form.get('description', '')
        status = request.form.get('status', 'pending')
        update_task(task_id, title, description, status)
        flash("Task updated successfully!", "success")
        return redirect(url_for('view_task', task_id=task_id))

    return render_template('edit_task.html', task=task)


@app.route('/task/<int:task_id>/delete', methods=['POST'])
def delete_task(task_id):
    """Handle deletion of a task."""
    redirect_resp = require_login()
    if redirect_resp:
        return redirect_resp

    task = get_task_by_id(task_id)
    if task is None:
        abort(404)

    delete_task_by_id(task_id)
    flash("Task deleted successfully!", "success")
    return redirect(url_for('tasks'))


# ---------------------------------------------------------------------------
# MAIN ENTRY POINT
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    app.run(debug=True)

