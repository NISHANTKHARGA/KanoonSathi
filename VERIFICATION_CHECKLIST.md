# KanoonSathi Database & Auth - Verification Checklist

## ✅ Installation & Setup

- [ ] Python 3 installed on system
- [ ] Flask installed: `pip install flask`
- [ ] Project folder: `c:\Users\Acer\Downloads\kanoon_sathi`
- [ ] Files present:
  - [ ] server.py (backend)
  - [ ] app.js (frontend)
  - [ ] signup.html
  - [ ] login.html
  - [ ] index.html
  - [ ] style.css

---

## ✅ Backend Verification

- [ ] Open terminal in project folder
- [ ] Run: `python server.py`
- [ ] See output:
  ```
  ✅ Database ready at: .../users.db
  🚀 KanoonSathi server running!
     Open: http://127.0.0.1:5000
  ```
- [ ] No errors in terminal
- [ ] Server stays running (don't close terminal)

---

## ✅ Database Creation

- [ ] File `users.db` appears in project folder
- [ ] Database has `users` table with columns:
  - [ ] id (auto-increment)
  - [ ] name
  - [ ] email (unique)
  - [ ] password (hashed)
  - [ ] role
  - [ ] token
  - [ ] created_at

---

## ✅ Signup Functionality Test

**Test 1: Create First Account**

1. [ ] Open browser: `http://127.0.0.1:5000`
2. [ ] Click "Signup" button
3. [ ] Fill form:
   - [ ] Name: `Test User`
   - [ ] Email: `test@example.com`
   - [ ] Password: `testpass123`
   - [ ] Role: `User`
4. [ ] Click "Sign Up"
5. [ ] See: "Registration successful"
6. [ ] Auto-redirected to home page
7. [ ] See: "Welcome Test User" or similar

**Test 2: Try Duplicate Signup**

1. [ ] Go to signup again
2. [ ] Use same email: `test@example.com`
3. [ ] Different password
4. [ ] Click "Sign Up"
5. [ ] See error: "An account with this email already exists"

**Test 3: Invalid Password**

1. [ ] Go to signup
2. [ ] Email: `test2@example.com`
3. [ ] Password: `short` (less than 6 chars)
4. [ ] Click "Sign Up"
5. [ ] See error: "Password must be at least 6 characters"

---

## ✅ Login Functionality Test

**Test 1: Successful Login**

1. [ ] Logout if needed
2. [ ] Go to: `http://127.0.0.1:5000/login.html`
3. [ ] Enter credentials:
   - [ ] Email: `test@example.com`
   - [ ] Password: `testpass123`
   - [ ] Role: `User`
4. [ ] Click "Login"
5. [ ] Auto-redirected to home
6. [ ] Logged in (token in localStorage)

**Test 2: Wrong Password**

1. [ ] Go to login
2. [ ] Enter:
   - [ ] Email: `test@example.com`
   - [ ] Password: `wrongpassword`
   - [ ] Role: `User`
3. [ ] Click "Login"
4. [ ] See error: "Incorrect password"
5. [ ] Stays on login page (not logged in)

**Test 3: Non-existent Email**

1. [ ] Go to login
2. [ ] Enter:
   - [ ] Email: `nonexistent@example.com`
   - [ ] Password: `anypassword`
   - [ ] Role: `User`
3. [ ] Click "Login"
4. [ ] See error: "No account found"

**Test 4: Wrong Role**

1. [ ] Go to login
2. [ ] Enter:
   - [ ] Email: `test@example.com`
   - [ ] Password: `testpass123`
   - [ ] Role: `Lawyer` (different from signup)
3. [ ] Click "Login"
4. [ ] See error: "account is registered as user, not lawyer"

---

## ✅ Token & Session Test

**Test 1: Token Saved**

1. [ ] After login, press F12 (Developer Tools)
2. [ ] Go to Console
3. [ ] Type: `localStorage.getItem('token')`
4. [ ] See: Long hex string (64 characters)
5. [ ] Type: `localStorage.getItem('user')`
6. [ ] See: JSON object with id, name, email, role

**Test 2: Token Persists**

1. [ ] After login, refresh page (F5)
2. [ ] Still logged in
3. [ ] Navigation shows logged-in state

**Test 3: Logout Clears Token**

1. [ ] Click "Logout"
2. [ ] See: Redirect to login page
3. [ ] Press F12, check localStorage
4. [ ] Both 'token' and 'user' are empty

---

## ✅ API Endpoint Tests

**Test 1: POST /register**

```bash
curl -X POST http://127.0.0.1:5000/register \
  -H "Content-Type: application/json" \
  -d '{"name":"API Test","email":"api@test.com","password":"apitest123","role":"user"}'
```

- [ ] Returns: 201 status
- [ ] Response includes: id, name, email, role, token

**Test 2: POST /login**

```bash
curl -X POST http://127.0.0.1:5000/login \
  -H "Content-Type: application/json" \
  -d '{"email":"api@test.com","password":"apitest123","role":"user"}'
```

- [ ] Returns: 200 status
- [ ] Response includes: id, name, email, role, token

**Test 3: GET /api/users**

```bash
curl http://127.0.0.1:5000/api/users
```

- [ ] Returns: 200 status
- [ ] See JSON list of all registered users

**Test 4: GET /api/me (with token)**

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" http://127.0.0.1:5000/api/me
```

- [ ] Returns: 200 status
- [ ] Response includes current user info

---

## ✅ Security Verification

- [ ] Passwords NOT visible in database (all hashed)
- [ ] Tokens are random 64-character hex strings
- [ ] Email addresses are unique (no duplicates)
- [ ] Password requires minimum 6 characters
- [ ] CORS headers present (can call API from frontend)

---

## ✅ File Integrity

- [ ] server.py: Complete (220+ lines)
- [ ] app.js: Has authentication helpers
- [ ] signup.html: Calls /register endpoint
- [ ] login.html: Calls /login endpoint
- [ ] README.md: Documentation present
- [ ] QUICK_START.md: Quick reference present

---

## ⚠️ Common Issues & Fixes

| Issue                    | Fix                                              |
| ------------------------ | ------------------------------------------------ |
| Port 5000 already in use | Change port in server.py or kill process on port |
| Module flask not found   | `pip install flask`                              |
| Database locked error    | Make sure no other instance is running           |
| "Cannot GET /"           | Server not running, run python server.py         |
| Token not saving         | Check browser localStorage, clear cache          |
| CORS error               | Ensure server has CORS enabled (it does)         |

---

## 📋 Final Checklist Summary

- [ ] **Installation**: Python & Flask ready
- [ ] **Server**: Running on port 5000
- [ ] **Database**: users.db created with correct schema
- [ ] **Signup**: Working with validation
- [ ] **Login**: Only registered users can login
- [ ] **Tokens**: Generated and saved correctly
- [ ] **Security**: Passwords hashed, emails unique
- [ ] **Frontend**: All pages loading correctly
- [ ] **Integration**: Frontend ↔ Backend communication working

---

## 🎉 You're Ready!

If all checkboxes are ✅, your KanoonSathi authentication system is:

- ✅ Installed correctly
- ✅ Running properly
- ✅ Secure
- ✅ Ready for production

**Next Steps**:

1. Add more features (appointments, lawyer profiles, etc.)
2. Deploy to production server
3. Set up email verification (optional)
4. Add password reset functionality (optional)
5. Implement 2FA (optional)
