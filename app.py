from flask import Flask, request, render_template, redirect, url_for, session, abort
import sqlite3

app = Flask(__name__)
app.secret_key = 'insecure-secret-key-for-demo'

DATABASE = 'database.db'

def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    with app.app_context():
        db = get_db()
        with open('schema.sql', 'r') as f:
            db.executescript(f.read())
        db.commit()

# Initialize DB on first request (or you can run it manually)
@app.before_request
def setup():
    if not hasattr(app, 'db_initialized'):
        init_db()
        app.db_initialized = True

# ----------------- AUTH ROUTES -----------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        try:
            db.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                       (username, password))
            db.commit()
        except sqlite3.IntegrityError:
            return "Username already exists"
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        # 🚨 VULNERABILITY 1: SQL Injection
        query = f"SELECT id FROM users WHERE username = '{username}' AND password = '{password}'"
        cursor = db.execute(query)
        user = cursor.fetchone()
        if user:
            session['user_id'] = user['id']
            return redirect(url_for('tasks'))
        else:
            return "Invalid credentials"
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

# ----------------- TASK ROUTES -----------------
@app.route('/tasks')
def tasks():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    db = get_db()
    tasks = db.execute("SELECT * FROM tasks WHERE user_id = ?",
                       (session['user_id'],)).fetchall()
    return render_template('tasks.html', tasks=tasks)

@app.route('/task/<int:task_id>')
def view_task(task_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    db = get_db()
    # 🚨 VULNERABILITY 3: IDOR – No ownership check
    task = db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if task is None:
        abort(404)
    # 🚨 VULNERABILITY 2: XSS – using |safe disables auto-escaping
    return render_template('task.html', task=task)

@app.route('/create', methods=['POST'])
def create_task():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    title = request.form['title']
    description = request.form.get('description', '')
    db = get_db()
    db.execute("INSERT INTO tasks (user_id, title, description) VALUES (?, ?, ?)",
               (session['user_id'], title, description))
    db.commit()
    return redirect(url_for('tasks'))

if __name__ == '__main__':
    app.run(debug=True)
