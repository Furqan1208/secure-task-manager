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

# Test login (also tests SQL injection vector is present via string formatting)
resp = client.post('/login', data={'username': 'testuser', 'password': 'testpass'}, follow_redirects=True)
assert b"Your Tasks" in resp.data or b"Tasks" in resp.data, f"Login failed: {resp.data[:200]}"
print("[PASS] Login works")

# Test task creation
resp = client.post('/create', data={'title': 'Test Task', 'description': 'A test description', 'status': 'pending'}, follow_redirects=True)
assert b"Test Task" in resp.data, "Task creation failed"
print("[PASS] Task creation works")

# Test tasks list
resp = client.get('/tasks')
assert resp.status_code == 200
assert b"Test Task" in resp.data
print("[PASS] Task list displays tasks")

# Test task detail (XSS vulnerability preserved via |safe)
resp = client.get('/task/1')
assert resp.status_code == 200
assert b"Test Task" in resp.data
print("[PASS] Task detail works")

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

# Verify all vulnerabilities are preserved by inspecting source code
with open('c:/SSDD/secure-task-manager/app.py', 'r') as f:
    app_content = f.read()
    assert "f\"SELECT id FROM users WHERE username = '{username}' AND password = '{password}'\"" in app_content, "SQL Injection vulnerability missing"
    assert "SELECT * FROM tasks WHERE id = ?" in app_content, "IDOR query missing"
    # Confirm no user_id is added to the get_task_by_id query
    idor_section = app_content.split("def get_task_by_id")[1].split("def delete_task_by_id")[0]
    assert "user_id" not in idor_section, "IDOR ownership check may have been added"

with open('c:/SSDD/secure-task-manager/templates/task.html', 'r') as f:
    task_html = f.read()
    assert "task.title | safe" in task_html, "XSS vulnerability (title | safe) missing"
    assert "task.description | safe" in task_html, "XSS vulnerability (description | safe) missing"

print("[PASS] All vulnerabilities preserved in source code")

print("\n=== ALL TESTS PASSED ===")

