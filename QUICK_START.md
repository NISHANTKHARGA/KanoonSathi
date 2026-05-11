# KanoonSathi - Quick Start Guide

## 🎯 In 3 Steps

### Step 1: Install Dependencies

```bash
pip install flask
```

### Step 2: Start the Server

```bash
python server.py
```

### Step 3: Open in Browser

```
http://127.0.0.1:5000
```

---

## 📖 User Flow

### New User (Signup)

1. Click "Signup" → Fill in details → Create account
2. Automatically logged in → Token saved to browser
3. Can now access all features

### Existing User (Login)

1. Click "Login" → Enter email & password → Click Login
2. Only registered users can log in
3. New token generated → Logged in status maintained

### Logout

- Click "Logout" in menu → Redirected to login page
- Browser storage cleared → Token removed

---

## 🗄️ Database Overview

**Location**: `users.db` (auto-created in project folder)

**What it stores**:

- User accounts (name, email, hashed password)
- User roles (user, lawyer, admin)
- Session tokens
- Registration timestamps

**Security**:

- Passwords are hashed (cannot be read)
- Tokens are unique (one per login)
- Email addresses are unique (no duplicates)

---

## ✨ Key Features Working

✅ User Registration with validation
✅ Secure Password Hashing
✅ Login Authentication
✅ Token-Based Sessions
✅ Role-Based Access (user/lawyer/admin)
✅ Google OAuth Support
✅ Automatic Token Management
✅ User Session Persistence

---

## 🧪 Test It Out

**Test Scenario 1: New User Signup**

```
1. Go to /signup.html
2. Enter: name=John, email=john@test.com, password=test123
3. Click Sign Up
4. See: "Registration successful"
5. Redirected to home page (logged in)
```

**Test Scenario 2: Login with Same Account**

```
1. Click Logout
2. Go to /login.html
3. Enter: john@test.com / test123
4. Click Login
5. Logged in successfully
```

**Test Scenario 3: Duplicate Email Prevention**

```
1. Try to signup with john@test.com again
2. See error: "Account already exists"
```

**Test Scenario 4: Wrong Password**

```
1. Try login with john@test.com / wrongpassword
2. See error: "Incorrect password"
```

---

## 📊 Database Check

To view all registered users, go to:

```
http://127.0.0.1:5000/api/users
```

You'll see a JSON list of all accounts.

---

## ⚙️ Configuration

**API Server**: `http://127.0.0.1:5000` (change in app.js if needed)
**Database**: `users.db` (auto-created)
**Secret Key**: `kanoonsathi-secret-key-2024` (in server.py)

---

## 🔧 Troubleshooting

| Issue                   | Solution                                   |
| ----------------------- | ------------------------------------------ |
| "Cannot GET /"          | Server not running. Run `python server.py` |
| "No module named flask" | Run `pip install flask`                    |
| Login not working       | Check browser console, clear cache         |
| Database not created    | Check folder permissions                   |
| Token not saving        | Check browser localStorage (F12)           |

---

## 📱 Frontend Pages

- **index.html** - Home page (public)
- **signup.html** - Registration (public)
- **login.html** - Login (public)
- **lawyers.html** - Browse lawyers (requires login)
- **appointments.html** - My appointments (requires login)
- **consult.html** - AI consultation (public)
- **admin.html** - Admin dashboard (admin role)

---

## 🚀 What's Next?

The authentication system is complete! You can now:

1. Add lawyer profiles and verification
2. Build appointment booking
3. Create AI chat integration
4. Add payment processing
5. Build admin dashboard features

All new features will automatically have access to authenticated user data through tokens.

---

## 💡 Remember

- **Passwords are hashed** - Never stored in plain text
- **Tokens are unique** - One token per login session
- **Emails are unique** - Prevents duplicate accounts
- **Roles matter** - Some features restricted to lawyer/admin roles
