# KanoonSathi - Database & Authentication Setup

## ✅ What's Implemented

Your application now has a complete **user registration and authentication system**:

### Database

- **SQLite Database** (`users.db`) - stores all registered users
- **Users Table** with fields: id, name, email, password (hashed), role, token, created_at

### Authentication Features

1. **User Registration** (`/register`) - Create new accounts with validation
2. **User Login** (`/login`) - Only registered users can sign in
3. **Password Hashing** - Passwords are securely hashed using SHA-256
4. **Token-Based Sessions** - Users receive a unique token after login
5. **Google OAuth Support** - Quick login via Google email
6. **Role-Based Access** - Support for 'user', 'lawyer', and 'admin' roles

---

## 🚀 Setup Instructions

### 1. Install Requirements

Make sure you have Python 3 installed, then install Flask:

```bash
pip install flask
```

### 2. Run the Server

Navigate to the project folder and start the server:

```bash
python server.py
```

You should see:

```
✅ Database ready at: .../users.db
🚀 KanoonSathi server running!
   Open: http://127.0.0.1:5000
   Signup: http://127.0.0.1:5000/signup.html
   Login:  http://127.0.0.1:5000/login.html
```

### 3. Test the Application

1. Open **http://127.0.0.1:5000** in your browser
2. Go to **Signup** and create a new account
3. Log in with your credentials on the **Login** page
4. Your token is automatically saved in browser storage

---

## 📋 API Endpoints

### Registration

```
POST /register
Body: { name, email, password, role }
Response: { id, name, email, role, token }
```

### Login

```
POST /login
Body: { email, password, role }
Response: { id, name, email, role, token }
```

### Google OAuth

```
POST /api/auth/google
Body: { email, name }
Response: { id, name, email, role, token }
```

### Get Current User

```
GET /api/me
Header: Authorization: Bearer <token>
Response: { id, name, email, role }
```

### View All Users (Debug)

```
GET /api/users
Response: [{ id, name, email, role, created_at }, ...]
```

---

## 🔒 Security Features

✅ **Password Hashing** - Passwords are never stored in plain text
✅ **Unique Emails** - Duplicate accounts are prevented
✅ **Token-Based Auth** - Tokens are random and secure (64-character hex)
✅ **Role Validation** - Login role must match registration role
✅ **Input Validation** - All fields are validated on the server
✅ **CORS Enabled** - Frontend can safely call the API

---

## 📁 File Structure

```
kanoon_sathi/
├── server.py              ← Main backend (COMPLETE)
├── app.js                 ← Frontend auth helpers
├── signup.html            ← Registration page
├── login.html             ← Login page
├── index.html             ← Home page
├── users.db               ← SQLite database (auto-created)
└── [other HTML/CSS files]
```

---

## 🧪 Testing Steps

### Test Registration

1. Navigate to http://127.0.0.1:5000/signup.html
2. Fill in form:
   - Name: `John Doe`
   - Email: `john@example.com`
   - Password: `password123`
   - Role: `User`
3. Click "Sign Up"
4. You should be logged in automatically

### Test Login

1. Log out using the menu
2. Navigate to http://127.0.0.1:5000/login.html
3. Enter same email and password
4. Click "Login"
5. You should be logged in

### Test Duplicate Prevention

1. Try to sign up with the same email again
2. You should see: "An account with this email already exists"

### Test Wrong Password

1. Log out
2. Try to login with wrong password
3. You should see: "Incorrect password"

---

## 💾 Database Schema

The `users` table stores:

| Column     | Type    | Notes                            |
| ---------- | ------- | -------------------------------- |
| id         | INTEGER | Primary key, auto-increment      |
| name       | TEXT    | Full name (required)             |
| email      | TEXT    | Email address (required, unique) |
| password   | TEXT    | SHA-256 hashed password          |
| role       | TEXT    | 'user', 'lawyer', or 'admin'     |
| token      | TEXT    | Session token (64-char hex)      |
| created_at | TEXT    | ISO format timestamp             |

---

## 🔑 How Authentication Works

1. User signs up → Password is hashed → User stored in database ✓
2. User attempts to login → Email is found → Password checked
3. If valid → New token generated → Token returned to frontend
4. Frontend saves token in localStorage (via KanoonAuth.saveAuth)
5. All future API calls auto-attach token in Authorization header
6. Backend validates token to confirm user identity

---

## 🛠️ Next Steps (Optional)

The backend is ready for additional features:

- Lawyer profiles and verification
- Appointment booking system
- AI consultation endpoint
- Rating and review system
- Payment integration

All these can be added by creating new endpoints in `server.py`.

---

## ❓ Troubleshooting

**Q: Getting "Cannot GET /" error?**

- Make sure the server is running and you're on `http://127.0.0.1:5000`

**Q: Database file not being created?**

- Check that you have write permissions in the project folder
- The database is created automatically on first run

**Q: "No module named 'flask'" error?**

- Run: `pip install flask`

**Q: Token not being saved in login?**

- Clear browser localStorage and try again
- Check browser console for any JavaScript errors

---

## 📞 Support

If you encounter any issues, check the terminal output - it will show detailed error messages.
