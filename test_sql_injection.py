"""
Test Script for SQL Injection Vulnerability
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
        # Fallback for Windows console
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

def test_sql_injection_login_bypass():
    """
    Test SQL injection vulnerability in login functionality
    Attempts to bypass authentication using SQL injection payloads
    """
    print("\n" + "="*60)
    print("TEST 1: SQL Injection - Authentication Bypass")
    print("="*60)
    
    # Test payloads that should bypass login if vulnerable
    sql_payloads = [
        ("admin' OR '1'='1' --", "any_password"),
        ("' OR 1=1 --", "anything"),
        ("admin' --", "test"),
        ("' OR '1'='1", "test"),
        ("admin' OR '1'='1'/*", "test"),
        ("' UNION SELECT 1,2,3 --", "test"),
    ]
    
    vulnerable_found = False

    # Ensure at least one valid user exists; otherwise OR-based SQLi may not
    # return any rows and can look falsely "safe" on an empty users table.
    seed_username = f"seed_sqli_{int(time.time())}"
    seed_password = "seedpass123"
    try:
        requests.post(
            f"{BASE_URL}/register",
            data={"username": seed_username, "password": seed_password},
            timeout=REQUEST_TIMEOUT
        )
    except Exception:
        pass
    
    for username, password in sql_payloads:
        print(f"\n[*] Testing payload: username='{username}', password='{password}'")
        
        try:
            response = requests.post(
                f"{BASE_URL}/login",
                data={"username": username, "password": password},
                allow_redirects=False,
                timeout=REQUEST_TIMEOUT
            )
            
            # Check if login was successful (redirect to /tasks means success)
            if response.status_code == 302 and "/tasks" in response.headers.get('Location', ''):
                print_status("⚠️", f"VULNERABLE: SQL injection successful! Bypassed login with: {username}")
                vulnerable_found = True
            else:
                print_status("✓", "Login failed as expected")
                
        except requests.exceptions.ConnectionError:
            print_status("✗", f"Cannot connect to {BASE_URL}. Is the app running?")
            return False
        except Exception as e:
            print_status("✗", f"Error: {e}")
    
    print("\n" + "-"*60)
    if vulnerable_found:
        print_status("❌", "TEST FAILED: SQL Injection vulnerability EXISTS")
        print("   (This is expected for vulnerable version)")
        return False
    else:
        print_status("✅", "TEST PASSED: No SQL injection vulnerability detected")
        print("   (This is expected for fixed version)")
        return True

def test_sql_injection_data_extraction():
    """
    Test if SQL injection can extract sensitive data
    Attempts to use UNION attack to extract user data
    """
    print("\n" + "="*60)
    print("TEST 2: SQL Injection - Data Extraction")
    print("="*60)
    
    # First, register a test user
    test_username = f"testuser_sqli_{int(time.time())}"
    test_password = "testpass123"
    
    try:
        # Register user
        requests.post(f"{BASE_URL}/register", data={
            "username": test_username,
            "password": test_password
        }, timeout=REQUEST_TIMEOUT)
        
        # Attempt UNION injection to extract data
        union_payload = "' UNION SELECT id, username, password FROM users --"
        
        response = requests.post(
            f"{BASE_URL}/login",
            data={"username": union_payload, "password": "anything"},
            allow_redirects=False,
            timeout=REQUEST_TIMEOUT
        )
        
        # Check response for extracted data
        if response.status_code == 302:
            # Follow redirect to tasks page to check if we're logged in
            session = requests.Session()
            session.post(
                f"{BASE_URL}/login",
                data={"username": union_payload, "password": "anything"},
                timeout=REQUEST_TIMEOUT
            )
            tasks_response = session.get(f"{BASE_URL}/tasks", timeout=REQUEST_TIMEOUT)
            
            # Look for signs of extracted data in response
            if test_username in tasks_response.text or "username" in tasks_response.text:
                print_status("⚠️", "VULNERABLE: SQL injection extracted user data!")
                print("    Detected potential data extraction")
                print_status("❌", "TEST FAILED: SQL injection allows data extraction")
                return False
        
        print_status("✓", "No data extraction detected")
        print_status("✅", "TEST PASSED: SQL injection does not allow data extraction")
        return True
        
    except Exception as e:
        print_status("✗", f"Error during test: {e}")
        return True

def run_sql_injection_tests():
    """Run all SQL injection tests"""
    print("\n" + "="*60)
    print("STARTING SQL INJECTION TESTS")
    print("="*60)
    
    test1_result = test_sql_injection_login_bypass()
    test2_result = test_sql_injection_data_extraction()
    
    print("\n" + "="*60)
    print("SQL INJECTION TEST SUMMARY")
    print("="*60)
    
    if not test1_result or not test2_result:
        print_status("❌", "OVERALL: SQL INJECTION VULNERABILITIES DETECTED")
        print("   This matches expected behavior for VULNERABLE version")
        return False
    else:
        print_status("✅", "OVERALL: No SQL injection vulnerabilities detected")
        print("   This matches expected behavior for FIXED version")
        return True

if __name__ == "__main__":
    print("\n[IMPORTANT] Make sure the Flask app is running on " + BASE_URL)
    print("   Start the app with: python app.py")
    try:
        input("\nPress Enter to start tests...")
    except EOFError:
        print("\n[INFO] Non-interactive mode detected, starting tests automatically...")
    
    success = run_sql_injection_tests()
    sys.exit(0 if success else 1)
