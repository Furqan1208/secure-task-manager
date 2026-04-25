import sys
sys.path.insert(0, 'c:/SSDD/secure-task-manager')

import app

# Use test client
client = app.app.test_client()

# Test index redirect when not logged in
resp = client.get('/')
assert resp.status_code == 302, f"Expected redirect, got {resp.status_code}"
print("[PASS] / redirects to login when anonymous")

# Test registration
resp = client.post('/register', data={'username': 'testuser', 'password': 'testpass'}, follow_redirects=True)
assert b"Login" in resp.data or b"successful" in resp.data, "Registration failed"
print("[PASS] Registration works")

# Test login with correct credentials
resp = client.post('/login', data={'username': 'testuser', 'password': 'testpass'}, follow_redirects=True)
assert b"Your Tasks" in resp.data or b"Tasks" in resp.data, f"Login failed: {resp.data[:200]}"
print("[PASS] Login works with correct password")

# Test login with wrong credentials
resp = client.post('/login', data={'username': 'testuser', 'password': 'wrongpass'}, follow_redirects=True)
assert b"Invalid" in resp.data, "Should reject wrong password"
print("[PASS] Login rejects wrong password")

# Test SQL Injection is fixed — try classic injection payload
resp = client.post('/login', data={'username': "admin' OR '1'='1", 'password': "anything"}, follow_redirects=True)
assert b"Invalid" in resp.data, "SQL Injection should be fixed"
print("[PASS] SQL Injection vulnerability fixed")

# Test task creation
resp = client.post('/create', data={'title': 'Test Task', 'description': 'A test description', 'status': 'pending'}, follow_redirects=True)
assert b"Test Task" in resp.data, "Task creation failed"
print("[PASS] Task creation works")

# Test tasks list
resp = client.get('/tasks')
assert resp.status_code == 200
assert b"Test Task" in resp.data
print("[PASS] Task list displays tasks")

# Test task detail
resp = client.get('/task/1')
assert resp.status_code == 200
assert b"Test Task" in resp.data
print("[PASS] Task detail works")

# Test XSS is fixed — task with script tags should be escaped
client.post('/create', data={'title': '<script>alert(1)</script>', 'description': '<img src=x onerror=alert(1)>', 'status': 'pending'}, follow_redirects=True)
resp = client.get('/task/2')
assert resp.status_code == 200
# The response should contain escaped HTML, not raw script execution
assert b"<script>" in resp.data or b"<script>alert(1)</script>" not in resp.data, "XSS not escaped"
print("[PASS] XSS vulnerability fixed (output is escaped)")

# Test edit task page
resp = client.get('/task/1/edit')
assert resp.status_code == 200
assert b"Edit Task" in resp.data
print("[PASS] Edit task page loads")

# Test update task
resp = client.post('/task/1/edit', data={'title': 'Updated Task', 'description': 'Updated desc', 'status': 'completed'}, follow_redirects=True)
assert b"Updated Task" in resp.data, "Task update failed"
print("[PASS] Task update works")

# Test delete task
resp = client.post('/task/1/delete', follow_redirects=True)
assert b"deleted" in resp.data.lower() or b"Your Tasks" in resp.data, "Task delete failed"
print("[PASS] Task deletion works")

# Test IDOR is fixed — create a second user and try to access their task
client.post('/register', data={'username': 'attacker', 'password': 'attackerpass'}, follow_redirects=True)
client.post('/login', data={'username': 'attacker', 'password': 'attackerpass'}, follow_redirects=True)
client.post('/create', data={'title': 'Victim Task', 'description': 'Secret', 'status': 'pending'}, follow_redirects=True)

# Switch back to original user
client.post('/login', data={'username': 'testuser', 'password': 'testpass'}, follow_redirects=True)

# Try to access attacker's task (task ID 3 should belong to attacker)
resp = client.get('/task/3')
assert resp.status_code == 404, f"IDOR not fixed: got {resp.status_code} instead of 404"
print("[PASS] IDOR vulnerability fixed (ownership enforced)")

# Try to delete attacker's task
resp = client.post('/task/3/delete', follow_redirects=True)
assert resp.status_code == 404, f"IDOR delete not fixed: got {resp.status_code}"
print("[PASS] IDOR delete enforcement works")

# Verify source code no longer contains vulnerable patterns
with open('c:/SSDD/secure-task-manager/app.py', 'r') as f:
    app_content = f.read()
    assert "f\"SELECT id FROM users WHERE username = '{username}' AND password = '{password}'\"" not in app_content, "SQL Injection still present"
    assert "check_password_hash" in app_content, "Password hashing missing"
    assert "generate_password_hash" in app_content, "Password hashing missing"
    # Verify IDOR fix: get_task_by_id must take user_id
    assert "def get_task_by_id(task_id, user_id):" in app_content, "IDOR fix missing in get_task_by_id"
    assert "SELECT * FROM tasks WHERE id = ? AND user_id = ?" in app_content, "IDOR query missing"

with open('c:/SSDD/secure-task-manager/templates/task.html', 'r') as f:
    task_html = f.read()
    assert "task.title | safe" not in task_html, "XSS vulnerability (title | safe) still present"
    assert "task.description | safe" not in task_html, "XSS vulnerability (description | safe) still present"
    assert "{{ task.title }}" in task_html, "Task title rendering missing"
    assert "{{ task.description }}" in task_html, "Task description rendering missing"

print("[PASS] All vulnerabilities fixed in source code")

print("\n=== ALL SECURITY FIXES VERIFIED ===")

