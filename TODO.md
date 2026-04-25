# Secure Task Manager — FIXED Branch

## Security Fixes
- [ ] Fix SQL Injection in login route (parameterized query)
- [ ] Fix XSS in task.html (remove `|safe` filters)
- [ ] Fix IDOR in task access (enforce user_id ownership)
- [ ] Fix hardcoded secret key (use `os.urandom`)
- [ ] Fix plaintext passwords (use Werkzeug hashing)
- [ ] Add basic input validation
- [ ] Update tests to verify all fixes
- [ ] Run full test suite

