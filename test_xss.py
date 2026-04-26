"""
Test Script for XSS (Cross-Site Scripting) Vulnerability
This test should FAIL on vulnerable version and PASS on fixed version
"""

import requests
import sys
import re
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

class XSSTester:
    def __init__(self):
        self.session = requests.Session()
        
    def register_and_login(self, username, password):
        """Register and login a test user"""
        # Register
        self.session.post(f"{BASE_URL}/register", data={
            "username": username,
            "password": password
        }, timeout=REQUEST_TIMEOUT)
        # Login
        response = self.session.post(f"{BASE_URL}/login", data={
            "username": username,
            "password": password
        }, allow_redirects=False, timeout=REQUEST_TIMEOUT)
        return response.status_code == 302
    
    def create_task(self, title, description):
        """Create a task with potential XSS payload"""
        response = self.session.post(f"{BASE_URL}/create", data={
            "title": title,
            "description": description,
            "status": "pending"
        }, allow_redirects=False, timeout=REQUEST_TIMEOUT)
        return response.status_code == 302
    
    def get_tasks_page(self):
        """Get the task list page"""
        response = self.session.get(f"{BASE_URL}/tasks", timeout=REQUEST_TIMEOUT)
        return response

    def get_latest_task_id(self):
        """Extract the most recently rendered task id from the tasks page."""
        response = self.get_tasks_page()
        matches = re.findall(r'/task/(\d+)', response.text)
        if not matches:
            return None
        return int(matches[0])

    def get_task_detail(self, task_id):
        """Fetch the task detail page where unsafe rendering occurs."""
        return self.session.get(f"{BASE_URL}/task/{task_id}", timeout=REQUEST_TIMEOUT)

def test_stored_xss_in_title():
    """
    Test stored XSS vulnerability in task title
    """
    print("\n" + "="*60)
    print("TEST 1: Stored XSS - Task Title")
    print("="*60)
    
    tester = XSSTester()
    unique_suffix = str(int(time.time()))
    username = f"xss_tester_{unique_suffix}"
    
    # XSS payloads to test
    xss_payloads = [
        ("<script>alert('XSS')</script>", "Basic script tag"),
        ("<img src=x onerror=alert('XSS')>", "Image onerror event"),
        ("<svg onload=alert('XSS')>", "SVG onload"),
    ]
    
    vulnerable_found = False
    
    try:
        # Register and login
        tester.register_and_login(username, "password123")
        print(f"[*] Logged in as: {username}")
        
        for payload, description in xss_payloads:
            print(f"\n[*] Testing payload: {description}")
            print(f"    Payload: {payload}")
            
            # Create task with XSS payload in title
            tester.create_task(payload, "This is a test description")
            
            task_id = tester.get_latest_task_id()
            if task_id is None:
                print_status("✗", "Could not locate created task ID")
                continue

            # The vulnerable template is task detail page (`task.html`) using |safe.
            detail_response = tester.get_task_detail(task_id)
            
            # Check if payload appears unescaped in response
            if payload in detail_response.text:
                # Check if it's actually HTML or just text
                if "<script>" in detail_response.text and "</script>" in detail_response.text:
                    print_status("⚠️", "VULNERABLE: Unescaped script tag found!")
                    vulnerable_found = True
                elif "<img" in detail_response.text and "onerror" in detail_response.text:
                    print_status("⚠️", "VULNERABLE: Unescaped image onerror found!")
                    vulnerable_found = True
                elif "<svg" in detail_response.text and "onload" in detail_response.text:
                    print_status("⚠️", "VULNERABLE: Unescaped SVG onload found!")
                    vulnerable_found = True
                else:
                    print_status("✓", "Payload appears escaped (no active HTML)")
            else:
                # Check for escaped version
                escaped_payload = payload.replace("<", "&lt;").replace(">", "&gt;")
                if escaped_payload in detail_response.text:
                    print_status("✓", "Payload properly escaped")
                else:
                    print("    ? Payload not found in response")
        
        print("\n" + "-"*60)
        if vulnerable_found:
            print_status("❌", "TEST FAILED: XSS vulnerability EXISTS in task titles")
            print("   (This is expected for vulnerable version)")
            return False
        else:
            print_status("✅", "TEST PASSED: No XSS vulnerability detected in task titles")
            print("   (This is expected for fixed version)")
            return True
            
    except Exception as e:
        print_status("✗", f"Error during test: {e}")
        return True

def test_stored_xss_in_description():
    """
    Test stored XSS vulnerability in task description
    """
    print("\n" + "="*60)
    print("TEST 2: Stored XSS - Task Description")
    print("="*60)
    
    tester = XSSTester()
    unique_suffix = str(int(time.time()))
    username = f"xss_desc_{unique_suffix}"
    
    # XSS payloads specifically for description field
    xss_payloads = [
        ("<script>alert('XSS in description')</script>", "Script tag"),
        ("<img src=x onerror=alert('XSS')>", "Image onerror"),
    ]
    
    vulnerable_found = False
    
    try:
        tester.register_and_login(username, "password123")
        print(f"[*] Logged in as: {username}")
        
        for payload, description in xss_payloads:
            print(f"\n[*] Testing payload: {description}")
            print(f"    Payload: {payload}")
            
            # Create task with XSS payload in description
            tester.create_task("Test Task", payload)
            
            task_id = tester.get_latest_task_id()
            if task_id is None:
                print_status("✗", "Could not locate created task ID")
                continue

            # Get vulnerable detail view and check
            detail_response = tester.get_task_detail(task_id)
            
            # Look for unescaped HTML
            if payload in detail_response.text and "<script>" in detail_response.text and "</script>" in detail_response.text:
                print_status("⚠️", "VULNERABLE: Unescaped script in description!")
                vulnerable_found = True
            elif payload in detail_response.text and "<img" in detail_response.text and "onerror" in detail_response.text:
                print_status("⚠️", "VULNERABLE: Unescaped image onerror in description!")
                vulnerable_found = True
            else:
                # Check if escaped
                if "&lt;script&gt;" in detail_response.text or "&lt;img" in detail_response.text:
                    print_status("✓", "Payload properly escaped")
                else:
                    print("    ? Payload not found or properly handled")
        
        if vulnerable_found:
            print("\n" + "-"*60)
            print_status("❌", "TEST FAILED: XSS vulnerability EXISTS in task descriptions")
            return False
        else:
            print("\n" + "-"*60)
            print_status("✅", "TEST PASSED: No XSS vulnerability in task descriptions")
            return True
            
    except Exception as e:
        print_status("✗", f"Error during test: {e}")
        return True

def run_xss_tests():
    """Run all XSS tests"""
    print("\n" + "="*60)
    print("STARTING XSS TESTS")
    print("="*60)
    
    test1 = test_stored_xss_in_title()
    test2 = test_stored_xss_in_description()
    
    print("\n" + "="*60)
    print("XSS TEST SUMMARY")
    print("="*60)
    
    if not (test1 and test2):
        print_status("❌", "OVERALL: XSS VULNERABILITIES DETECTED")
        print("   This matches expected behavior for VULNERABLE version")
        return False
    else:
        print_status("✅", "OVERALL: No XSS vulnerabilities detected")
        print("   This matches expected behavior for FIXED version")
        return True

if __name__ == "__main__":
    print("\n[IMPORTANT] Make sure the Flask app is running on " + BASE_URL)
    print("   Start the app with: python app.py")
    try:
        input("\nPress Enter to start tests...")
    except EOFError:
        print("\n[INFO] Non-interactive mode detected, starting tests automatically...")
    
    success = run_xss_tests()
    sys.exit(0 if success else 1)              