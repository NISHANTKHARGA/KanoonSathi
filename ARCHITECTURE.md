# KanoonSathi Architecture & Integration

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER BROWSER                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────┐  ┌──────────────────┐  ┌─────────────┐   │
│  │  signup.html     │  │  login.html      │  │ index.html  │   │
│  │  Register form   │  │  Login form      │  │   Home page │   │
│  └────────┬─────────┘  └────────┬─────────┘  └──────┬──────┘   │
│           │                     │                    │            │
│           └─────────────────────┼────────────────────┘            │
│                                 │                                  │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │              app.js (Frontend Helpers)                    │    │
│  │                                                            │    │
│  │  • fetchJson() - API calls with auto token              │    │
│  │  • KanoonAuth - Login/logout management                 │    │
│  │  • localStorage - Token storage                         │    │
│  │  • escapeHtml() - XSS prevention                        │    │
│  └──────────────────────┬───────────────────────────────────┘    │
│                         │                                          │
└─────────────────────────┼──────────────────────────────────────────┘
                          │
                      HTTP/REST
         (JSON requests with Authorization token)
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                   FLASK SERVER (server.py)                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Routes:                                                          │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  POST /register      → Create new user account         │     │
│  │  POST /login         → Authenticate user               │     │
│  │  POST /api/auth/google → Google OAuth login           │     │
│  │  GET  /api/me        → Verify token & get user info   │     │
│  │  GET  /api/users     → List all users                 │     │
│  │  GET  /<path>        → Serve HTML/CSS/JS files        │     │
│  └────────────────────────────────────────────────────────┘     │
│                         │                                         │
│  Security Layer:        │                                         │
│  ├─ hash_password()     │                                         │
│  ├─ check_password()    │                                         │
│  ├─ generate_token()    │                                         │
│  └─ validate_input()    │                                         │
│                         │                                         │
└─────────────────────────┼─────────────────────────────────────────┘
                          │
                       SQLite
                  (SQL queries)
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│              DATABASE (users.db - SQLite)                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Table: users                                                     │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ id    │ name   │ email          │ password   │ role     │    │
│  ├───────┼────────┼────────────────┼────────────┼──────────┤    │
│  │ 1     │ John   │ john@...       │ [HASHED]   │ user     │    │
│  │ 2     │ Jane   │ jane@...       │ [HASHED]   │ lawyer   │    │
│  │ 3     │ Admin  │ admin@...      │ [HASHED]   │ admin    │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
│  Also stores: token (session), created_at (timestamp)           │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 Data Flow Diagrams

### Signup Flow

```
User fills form           Server validates          Database stores
(name, email,      →      (input check,      →      (new user record
 password, role)          email unique,              with hashed
                          hash password)             password)
                                                            │
                                                            ▼
                                                     Generate token
                                                            │
                                                            ▼
                          Return to frontend ←      Send user info
                                │                  & token to client
                                │
                                ▼
                         Save to localStorage
                                │
                                ▼
                           Auto-redirect
                          to home (logged in)
```

### Login Flow

```
User enters           Server finds           Check password    Generate
credentials    →      user by email    →     against hash  →  new token
(email, pass,         (select from db)       (if match)          │
 role)                      │                                     ▼
                            │                              Update token
                            ▼                             in database
                     Found? (Yes/No)
                     │         │
                 Yes │         │ No
                     │         └──→ Return error
                     │              "No account"
                     ▼
              Return token
                   & user info
                     │
                     ▼
           Save to localStorage
                     │
                     ▼
            Redirect to home
```

### Automatic Token Attachment

```
User clicks button    Frontend sends      Server receives    Database
(e.g., My          →  API request with  →  request &    →   query
Appointments)         auto-attached token   validates token   with
                      (in header)           (check token)      user data
                            │                      │
                            │                      ▼
                            │              Token matches user
                            │                      │
                            └──────────────────────┤
                                                   ▼
                                         Return user's data
                                         (appointments, etc.)
```

---

## 🔐 Security Layers

```
┌─────────────────────────────────────────────────────────┐
│ Layer 1: Frontend Validation                            │
│ • Email format check                                    │
│ • Password length check                                 │
│ • Field required check                                  │
│ • XSS prevention (escapeHtml)                          │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ Layer 2: Server Input Validation                        │
│ • Validate name not empty                              │
│ • Validate email format                                │
│ • Validate password ≥ 6 chars                          │
│ • Validate role in (user, lawyer, admin)              │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ Layer 3: Database Constraints                           │
│ • Email UNIQUE (no duplicates)                         │
│ • NOT NULL constraints                                  │
│ • Default role = 'user'                                │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ Layer 4: Cryptographic Security                        │
│ • SHA-256 password hashing                             │
│ • 64-character random tokens                           │
│ • Different token per login                            │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ Layer 5: Session Management                            │
│ • Token stored in localStorage (client)                │
│ • Token stored in database (server)                    │
│ • Auto-attach token to all API requests                │
│ • Server validates token on each request               │
└─────────────────────────────────────────────────────────┘
```

---

## 📝 Database Schema

```sql
-- Users Table
CREATE TABLE users (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,    -- Auto-increment ID
    name       TEXT NOT NULL,                        -- User's full name
    email      TEXT NOT NULL UNIQUE,                 -- Email (no duplicates)
    password   TEXT NOT NULL,                        -- SHA-256 hashed
    role       TEXT NOT NULL DEFAULT 'user',         -- user/lawyer/admin
    token      TEXT,                                 -- Current session token
    created_at TEXT NOT NULL                         -- ISO timestamp
);

-- Sample Data
INSERT INTO users VALUES (
    1,                                    -- id
    'John Doe',                          -- name
    'john@example.com',                  -- email
    'a665a45920422f...(64 chars)',       -- password (hashed)
    'user',                              -- role
    '3f7e9c2b...(64 chars)',             -- token
    '2026-05-11T12:00:00.000000'        -- created_at
);
```

---

## 🔄 Token Generation & Usage

```
┌─ generate_token() ─────────────────────────────┐
│                                                 │
│  secrets.token_hex(32)                         │
│  ↓                                              │
│  Generates 64-character random hex string      │
│  Example: "a1b2c3d4e5f6g7h8..."               │
│  ↓                                              │
│  Unique per login (different each time)        │
│                                                 │
└─────────────────────────────────────────────────┘

Usage:
  Register → Generate token → Store & return
  Login    → Generate new token → Store & return
  API call → Client sends token in header
  Server   → Verify token matches database

Request Header:
  Authorization: Bearer a1b2c3d4e5f6g7h8i9j0...
  ↑
  Token auto-attached by app.js fetchJson()
```

---

## 🚀 Integration Points

```
┌───────────────────────────────────────────────────────────┐
│ Frontend (HTML/JS)                    Backend (Python)    │
├───────────────────────────────────────────────────────────┤
│                                                             │
│ signup.html           ←→  POST /register                  │
│ ├─ name field              ├─ validate input              │
│ ├─ email field             ├─ hash password               │
│ ├─ password field          ├─ generate token              │
│ └─ role select             └─ insert to database          │
│      ↓ (sends JSON)                                        │
│      Returns {token}       Database ↔ users.db            │
│                                                             │
│ login.html            ←→  POST /login                     │
│ ├─ email field             ├─ find user                   │
│ ├─ password field          ├─ verify password             │
│ └─ role select             ├─ check role                  │
│      ↓ (sends JSON)        ├─ generate token              │
│      Returns {token}       └─ update database             │
│                                                             │
│ app.js (fetchJson)    ←→  GET /api/me                     │
│ ├─ attach token in        ├─ verify token                │
│ │  Authorization header   ├─ get user info               │
│ └─ send request           └─ return user object          │
│                                                             │
│ localStorage          ←→  Database tokens table           │
│ ├─ token              ├─ compare tokens                   │
│ ├─ user               ├─ session validation               │
│ └─ (persist state)    └─ (persist state)                  │
│                                                             │
└───────────────────────────────────────────────────────────┘
```

---

## 🧪 Request/Response Examples

### Example 1: Signup Request

```
POST /register HTTP/1.1
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "secure123",
  "role": "user"
}

Response (201 Created):
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "role": "user",
  "token": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2"
}
```

### Example 2: Login Request

```
POST /login HTTP/1.1
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "secure123",
  "role": "user"
}

Response (200 OK):
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "role": "user",
  "token": "b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3"
}
```

### Example 3: Protected API Request

```
GET /api/me HTTP/1.1
Authorization: Bearer b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6...

Response (200 OK):
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "role": "user"
}
```

---

## 📈 Scalability Considerations

```
Current Setup:
├─ SQLite (file-based) → Good for dev/small deployments
├─ Single server        → One process handling requests
└─ In-memory sessions   → Session data in database

For Scale:
├─ PostgreSQL/MySQL     → Better for multiple servers
├─ Redis/Memcached      → Session caching layer
├─ Load Balancer        → Distribute requests
├─ JWT Tokens           → Stateless authentication
└─ Kubernetes           → Container orchestration
```

---

## ✅ Complete Integration Checklist

- ✅ server.py - Backend complete
- ✅ app.js - Frontend helpers complete
- ✅ signup.html - Uses /register
- ✅ login.html - Uses /login
- ✅ All pages - Can access user info
- ✅ Database - users.db auto-created
- ✅ Security - All layers implemented
- ✅ CORS - Enabled for API calls
- ✅ Documentation - Complete

---

**Status: ✅ FULLY INTEGRATED AND READY**
