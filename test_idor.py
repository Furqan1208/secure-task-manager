"""
Test Script for IDOR (Insecure Direct Object Reference) Vulnerability
This test should FAIL on vulnerable version and PASS on fixed version
"""

import requests
import sys
import time

BASE_URL = "http://localhost:5000"
REQUEST_TIMEOUT = 5

def print_status(symbol, message):
    """Print status messages compatible with Windows console"""
    try:
        print(f"{symbol} {message}")
    except UnicodeEncodeError:
        if symbol == "✓":
            print(f"[OK] {message}")
        elif symbol == "✗":
            print(f"[ERROR] {message}")
        elif symbol == "⚠️":
            print(f"[WARNING] {message}")
        elif symbol == "❌":
            print(f"[FAIL] {message}")
        elif symbol == "✅":
            print(f"[PASS] {message}")
        else:
            print(f"{symbol} {message}")

class TaskManagerClient:
    """Helper class to simulate user sessions"""
    def __init__(self):
        self.session = requests.Session()
        self.user_id = None
        
    def register(self, username, password):
        """Register a new user"""
        response = self.session.post(f"{BASE_URL}/register", data={
            "username": username,
            "password": password
        }, timeout=REQUEST_TIMEOUT)
        return response.status_code == 200
    
    def login(self, username, password):
        """Login a user"""
        response = self.session.post(f"{BASE_URL}/login", data={
            "username": username,
            "password": password
        }, allow_redirects=False, timeout=REQUEST_TIMEOUT)
        
        if response.status_code == 302:
            # Follow the redirect
            self.session.get(f"{BASE_URL}/tasks", timeout=REQUEST_TIMEOUT)
            return True
        return False
    
    def create_task(self, title, description):
        """Create a new task"""
        response = self.session.post(f"{BASE_URL}/create", data={
            "title": title,
            "description": description,
            "status": "pending"
        }, allow_redirects=False, timeout=REQUEST_TIMEOUT)
        return response.status_code == 302
    
    def get_task(self, task_id):
        """Get a specific task by ID"""
        response = self.session.get(f"{BASE_URL}/task/{task_id}", timeout=REQUEST_TIMEOUT)
        return response
    
    def edit_task(self, task_id, title, description):
        """Edit a task by ID"""
        response = self.session.post(f"{BASE_URL}/task/{task_id}/edit", data={
            "title": title,
            "description": description,
            "status": "pending"
        }, allow_redirects=False, timeout=REQUEST_TIMEOUT)
        return response
    
    def delete_task(self, task_id):
        """Delete a task by ID"""
        response = self.session.post(f"{BASE_URL}/task/{task_id}/delete", timeout=REQUEST_TIMEOUT)
        return response

def test_idor_view_other_users_task():
    """
    Test IDOR vulnerability - Viewing other user's tasks
    """
    print("\n" + "="*60)
    print("TEST 1: IDOR - Viewing Another User's Task")
    print("="*60)
    
    # Create two different users
    alice = TaskManagerClient()
    bob = TaskManagerClient()
    
    unique_suffix = str(int(time.time()))
    
    alice_username = f"alice_{unique_suffix}"
    bob_username = f"bob_{unique_suffix}"
    common_password = "password123"
    
    try:
        # Register and login as Alice
        print(f"\n[*] Registering Alice: {alice_username}")
        alice.register(alice_username, common_password)
        alice.login(alice_username, common_password)
        
        # Alice creates a private task
        task_title = "Alice's Secret Document"
        task_desc = "This is private information only Alice should see"
        alice.create_task(task_title, task_desc)
        print(f"[*] Alice created task: '{task_title}'")
        
        # Get all tasks to find the task ID
        tasks_response = alice.session.get(f"{BASE_URL}/tasks", timeout=REQUEST_TIMEOUT)
        task_id = 1  # Default assumption
        
        # Try to find the actual task ID from response
        if f'/task/' in tasks_response.text:
            # Extract task ID (simplified)
            import re
            match = re.search(r'/task/(\d+)', tasks_response.text)
            if match:
                task_id = int(match.group(1))
                print(f"[*] Found task ID: {task_id}")
        
        # Register and login as Bob
        print(f"\n[*] Registering Bob: {bob_username}")
        bob.register(bob_username, common_password)
        bob.login(bob_username, common_password)
        
        # Bob tries to view Alice's task
        print(f"[*] Bob attempting to view task ID {task_id}")
        response = bob.get_task(task_id)
        
        # Check if Bob can see Alice's task
        if response.status_code == 200:
            if task_title in response.text or "Alice's Secret" in response.text:
                print_status("⚠️", "VULNERABLE: Bob accessed Alice's task!")
                print("    Response contains Alice's private data")
                print_status("❌", "TEST FAILED: IDOR vulnerability allows viewing other user's tasks")
                return False
            else:
                print_status("✓", "Bob cannot see Alice's task data")
        elif response.status_code == 404:
            print_status("✓", "Access denied (404) - Proper authorization")
        else:
            print_status("✓", f"Access denied with status {response.status_code}")
        
        print_status("✅", "TEST PASSED: Cannot view other user's tasks")
        return True
        
    except Exception as e:
        print_status("✗", f"Error during test: {e}")
        return True

def test_idor_modify_other_users_task():
    """
    Test IDOR vulnerability - Modifying other user's tasks
    """
    print("\n" + "="*60)
    print("TEST 2: IDOR - Modifying Another User's Task")
    print("="*60)
    
    unique_suffix = str(int(time.time()))
    
    alice = TaskManagerClient()
    bob = TaskManagerClient()
    
    alice_username = f"alice_mod_{unique_suffix}"
    bob_username = f"bob_mod_{unique_suffix}"
    
    try:
        # Setup Alice with a task
        alice.register(alice_username, "password123")
        alice.login(alice_username, "password123")
        original_title = "Alice's Original Task"
        alice.create_task(original_title, "This should not be modified by Bob")
        print(f"[*] Alice created task: '{original_title}'")
        
        # Find task ID
        tasks_response = alice.session.get(f"{BASE_URL}/tasks", timeout=REQUEST_TIMEOUT)
        task_id = 1
        import re
        match = re.search(r'/task/(\d+)', tasks_response.text)
        if match:
            task_id = int(match.group(1))
            print(f"[*] Task ID: {task_id}")
        
        # Bob tries to modify Alice's task
        bob.register(bob_username, "password123")
        bob.login(bob_username, "password123")
        
        modified_title = "HACKED by Bob!"
        print(f"[*] Bob attempting to modify task ID {task_id}")
        response = bob.edit_task(task_id, modified_title, "Modified description")
        
        # Check if modification was allowed
        if response.status_code == 302:
            # Follow redirect and check if task was modified
            view_response = bob.get_task(task_id)
            if modified_title in view_response.text:
                print_status("⚠️", "VULNERABLE: Bob modified Alice's task!")
                print(f"    Task title changed to: {modified_title}")
                print_status("❌", "TEST FAILED: IDOR vulnerability allows modifying other user's tasks")
                return False
        
        print_status("✓", "Bob cannot modify Alice's task")
        print_status("✅", "TEST PASSED: Cannot modify other user's tasks")
        return True
        
    except Exception as e:
        print_status("✗", f"Error during test: {e}")
        return True

def test_idor_delete_other_users_task():
    """
    Test IDOR vulnerability - Deleting other user's tasks
    """
    print("\n" + "="*60)
    print("TEST 3: IDOR - Deleting Another User's Task")
    print("="*60)
    
    unique_suffix = str(int(time.time()))
    
    alice = TaskManagerClient()
    bob = TaskManagerClient()
    
    alice_username = f"alice_del_{unique_suffix}"
    bob_username = f"bob_del_{unique_suffix}"
    
    try:
        # Setup Alice with a task
        alice.register(alice_username, "password123")
        alice.login(alice_username, "password123")
        alice.create_task("Alice's Important Task", "Do not delete")
        print(f"[*] Alice created a task")
        
        # Find task ID
        tasks_response = alice.session.get(f"{BASE_URL}/tasks", timeout=REQUEST_TIMEOUT)
        task_id = 1
        import re
        match = re.search(r'/task/(\d+)', tasks_response.text)
        if match:
            task_id = int(match.group(1))
            print(f"[*] Task ID: {task_id}")
        
        # Bob tries to delete Alice's task
        bob.register(bob_username, "password123")
        bob.login(bob_username, "password123")
        
        print(f"[*] Bob attempting to delete task ID {task_id}")
        response = bob.delete_task(task_id)
        
        # Check if task still exists for Alice
        alice_check = alice.get_task(task_id)
        
        if alice_check.status_code == 404 or "not found" in alice_check.text.lower():
            print_status("⚠️", "VULNERABLE: Bob deleted Alice's task!")
            print("    Task no longer exists")
            print_status("❌", "TEST FAILED: IDOR vulnerability allows deleting other user's tasks")
            return False
        
        print_status("✓", "Bob cannot delete Alice's task")
        print_status("✅", "TEST PASSED: Cannot delete other user's tasks")
        return True
        
    except Exception as e:
        print_status("✗", f"Error during test: {e}")
        return True

def run_idor_tests():
    """Run all IDOR tests"""
    print("\n" + "="*60)
    print("STARTING IDOR TESTS")
    print("="*60)
    
    test1 = test_idor_view_other_users_task()
    test2 = test_idor_modify_other_users_task()
    test3 = test_idor_delete_other_users_task()
    
    print("\n" + "="*60)
    print("IDOR TEST SUMMARY")
    print("="*60)
    
    if not (test1 and test2 and test3):
        print_status("❌", "OVERALL: IDOR VULNERABILITIES DETECTED")
        print("   This matches expected behavior for VULNERABLE version")
        return False
    else:
        print_status("✅", "OVERALL: No IDOR vulnerabilities detected")
        print("   This matches expected behavior for FIXED version")
        return True

if __name__ == "__main__":
    print("\n[IMPORTANT] Make sure the Flask app is running on " + BASE_URL)
    print("   Start the app with: python app.py")
    try:
        input("\nPress Enter to start tests...")
    except EOFError:
        print("\n[INFO] Non-interactive mode detected, starting tests automatically...")
    
    success = run_idor_tests()
    sys.exit(0 if success else 1)
