"""
Master Test Runner for All Security Tests
Run this script to test all three vulnerabilities at once
"""

import subprocess
import sys
import time
import requests

BASE_URL = "http://localhost:5000"

def print_status(symbol, message):
    """Print status messages compatible with Windows console"""
    try:
        print(f"{symbol} {message}")
    except UnicodeEncodeError:
        if symbol == "✓" or symbol == "✅":
            print(f"[PASS] {message}")
        elif symbol == "✗" or symbol == "❌":
            print(f"[FAIL] {message}")
        elif symbol == "⚠️":
            print(f"[WARNING] {message}")
        else:
            print(f"{symbol} {message}")

def check_app_running():
    """Check if the Flask application is running"""
    try:
        response = requests.get(BASE_URL, timeout=2)
        return True
    except:
        return False

def print_banner():
    """Print test banner"""
    print("="*70)
    print("   SECURITY VULNERABILITY TEST SUITE")
    print("="*70)
    print("\nThis test suite will check for three vulnerabilities:")
    print("  1. SQL Injection")
    print("  2. IDOR (Insecure Direct Object References)")
    print("  3. XSS (Cross-Site Scripting)")
    print("\n[IMPORTANT NOTES]")
    print("  - These tests should FAIL on the VULNERABLE version")
    print("  - These tests should PASS on the FIXED version")
    print("  - Make sure the app is running before starting")
    print("="*70)

def run_test(test_file, test_name):
    """Run an individual test file"""
    print(f"\n{'='*70}")
    print(f"RUNNING: {test_name}")
    print(f"{'='*70}")
    
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            stdin=subprocess.DEVNULL,
            timeout=120
        )
        
        print(result.stdout)
        if result.stderr:
            print("ERROR OUTPUT:")
            print(result.stderr)
        
        # Return True if test passed (exit code 0)
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print(f"[ERROR] {test_name} timed out!")
        return False
    except Exception as e:
        print(f"[ERROR] Error running {test_name}: {e}")
        return False

def print_results(results):
    """Print final test results"""
    print("\n" + "="*70)
    print("FINAL TEST RESULTS")
    print("="*70)
    
    passed = 0
    failed = 0
    
    for test_name, passed_flag in results.items():
        if passed_flag:
            print(f"[PASS] {test_name}")
            passed += 1
        else:
            print(f"[FAIL] {test_name}")
            failed += 1
    
    print("-"*70)
    print(f"TOTAL: {passed} passed, {failed} failed, {passed+failed} run")
    print("="*70)
    
    # Interpretation based on which version we're testing
    print("\n[INTERPRETATION]")
    if failed > 0:
        print("  [WARNING] VULNERABILITIES DETECTED - This matches the VULNERABLE version")
        print("     Expected behavior for 'main' branch")
    else:
        print("  [PASS] NO VULNERABILITIES DETECTED - This matches the FIXED version")
        print("     Expected behavior for 'fixed' branch")
    
    return failed == 0

def main():
    """Main test runner"""
    print_banner()
    
    # Check if app is running
    print("\n[CHECK] Verifying application is running...")
    if not check_app_running():
        print("[ERROR] Application is not running on " + BASE_URL)
        print("\nPlease start the Flask application first:")
        print("  python app.py")
        print("\nThen run this test suite again.")
        sys.exit(1)
    
    print("[OK] Application is running\n")
    
    # Run all tests
    results = {}
    
    # Test 1: SQL Injection
    results["SQL Injection"] = run_test("test_sql_injection.py", "SQL Injection Tests")
    
    # Test 2: IDOR
    results["IDOR"] = run_test("test_idor.py", "IDOR Tests")
    
    # Test 3: XSS
    results["XSS"] = run_test("test_xss.py", "XSS Tests")
    
    # Print final results
    all_passed = print_results(results)
    
    # Exit with appropriate code
    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()