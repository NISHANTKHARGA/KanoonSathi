"""
KanoonSathi Backend Server
- SQLite database for user storage
- POST /register  → create new user (signup.html)
- POST /login     → authenticate user (login.html)
- Serves all HTML frontend files
- CORS enabled so frontend JS can call the API
"""

import sqlite3
import hashlib
import secrets
import json
import os
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory, g

# ── App setup ──────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, 'users.db')

app = Flask(__name__, static_folder=BASE_DIR)
app.config['SECRET_KEY'] = 'kanoonsathi-secret-key-2024'


# ── CORS: allow frontend HTML to call the API ──────────────────────────────────
@app.after_request
def add_cors(response):
    response.headers['Access-Control-Allow-Origin']  = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
    return response

@app.route('/', defaults={'path': ''}, methods=['OPTIONS'])
@app.route('/<path:path>', methods=['OPTIONS'])
def handle_options(path):
    return jsonify({}), 200


# ── Database setup ─────────────────────────────────────────────────────────────
def get_db():
    """Get database connection (one per request)"""
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row   # rows act like dicts
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Create the users, lawyers, and appointments tables if they don't exist"""
    db = sqlite3.connect(DB_PATH)

    # Users table
    db.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT    NOT NULL,
            email      TEXT    NOT NULL UNIQUE,
            password   TEXT    NOT NULL,
            role       TEXT    NOT NULL DEFAULT 'user',
            token      TEXT,
            created_at TEXT    NOT NULL
        )
    ''')

    # Lawyers table
    db.execute('''
        CREATE TABLE IF NOT EXISTS lawyers (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id          INTEGER NOT NULL,
            name             TEXT    NOT NULL,
            email            TEXT    NOT NULL UNIQUE,
            phone            TEXT    NOT NULL,
            district         TEXT    NOT NULL,
            legal_area       TEXT    NOT NULL,
            experience_years INTEGER NOT NULL,
            fee_npr          INTEGER NOT NULL,
            availability     TEXT    NOT NULL,
            languages        TEXT    NOT NULL,
            license_number   TEXT    NOT NULL,
            specialization   TEXT    NOT NULL,
            bio              TEXT    NOT NULL,
            photo            TEXT,
            document         TEXT,
            status           TEXT    NOT NULL DEFAULT 'pending',
            rating           REAL    DEFAULT 0.0,
            created_at       TEXT    NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Appointments table
    db.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id       INTEGER NOT NULL,
            lawyer_id     INTEGER NOT NULL,
            date          TEXT    NOT NULL,
            time          TEXT    NOT NULL,
            mode          TEXT    NOT NULL,
            issue_summary TEXT    NOT NULL,
            chat_summary  TEXT,
            status        TEXT    NOT NULL DEFAULT 'pending',
            created_at    TEXT    NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (lawyer_id) REFERENCES lawyers (id)
        )
    ''')

    db.commit()
    db.close()
    print(f"✅ Database ready at: {DB_PATH}")


# ── Password helpers ───────────────────────────────────────────────────────────
def hash_password(raw):
    """Hash a plain-text password using SHA-256"""
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()

def check_password(raw, hashed):
    """Check if plain password matches stored hash"""
    return hash_password(raw) == hashed

def generate_token():
    """Create a secure random session token"""
    return secrets.token_hex(32)


# ── Serve frontend HTML files ──────────────────────────────────────────────────
@app.route('/')
def serve_index():
    return send_from_directory(BASE_DIR, 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve any HTML, CSS, JS file from the same folder"""
    return send_from_directory(BASE_DIR, filename)


# ══════════════════════════════════════════════════════════════════════
# POST /register   ← called by signup.html
# Body: { name, email, password, role }
# ══════════════════════════════════════════════════════════════════════
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json(silent=True) or {}

    name     = (data.get('name') or '').strip()
    email    = (data.get('email') or '').strip().lower()
    password = (data.get('password') or '')
    role     = (data.get('role') or 'user')

    # ── Validation ────────────────────────────────────────────────────
    if not name:
        return jsonify({'error': 'Full name is required.'}), 400
    if not email or '@' not in email:
        return jsonify({'error': 'Valid email is required.'}), 400
    if not password or len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters.'}), 400
    if role not in ('user', 'lawyer', 'admin'):
        return jsonify({'error': 'Invalid role selected.'}), 400

    db = get_db()

    # ── Check if email already registered ────────────────────────────
    existing = db.execute(
        'SELECT id FROM users WHERE email = ?', (email,)
    ).fetchone()

    if existing:
        return jsonify({'error': 'An account with this email already exists. Please login instead.'}), 400

    # ── Create user ───────────────────────────────────────────────────
    hashed = hash_password(password)
    token  = generate_token()
    now    = datetime.utcnow().isoformat()

    cursor = db.execute(
        'INSERT INTO users (name, email, password, role, token, created_at) VALUES (?, ?, ?, ?, ?, ?)',
        (name, email, hashed, role, token, now)
    )
    db.commit()
    user_id = cursor.lastrowid

    print(f"✅ New user registered: {name} ({email}) as {role}")

    return jsonify({
        'id':    user_id,
        'name':  name,
        'email': email,
        'role':  role,
        'token': token,
    }), 201


# ══════════════════════════════════════════════════════════════════════
# POST /login   ← called by login.html
# Body: { email, password, role }
# ══════════════════════════════════════════════════════════════════════
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}

    email    = (data.get('email') or '').strip().lower()
    password = (data.get('password') or '')
    role     = (data.get('role') or 'user')

    # ── Validation ────────────────────────────────────────────────────
    if not email or not password:
        return jsonify({'error': 'Email and password are required.'}), 400

    db = get_db()

    # ── Find user by email ────────────────────────────────────────────
    user = db.execute(
        'SELECT * FROM users WHERE email = ?', (email,)
    ).fetchone()

    if not user:
        return jsonify({'error': 'No account found with this email. Please sign up first.'}), 401

    # ── Check password ────────────────────────────────────────────────
    if not check_password(password, user['password']):
        return jsonify({'error': 'Incorrect password. Please try again.'}), 401

    # ── Check role matches ────────────────────────────────────────────
    if user['role'] != role:
        return jsonify({
            'error': f'This account is registered as "{user["role"]}", not "{role}". Please select the correct role.'
        }), 403

    # ── Refresh token on every login ──────────────────────────────────
    new_token = generate_token()
    db.execute('UPDATE users SET token = ? WHERE id = ?', (new_token, user['id']))
    db.commit()

    print(f"✅ User logged in: {user['name']} ({email}) as {role}")

    return jsonify({
        'id':    user['id'],
        'name':  user['name'],
        'email': user['email'],
        'role':  user['role'],
        'token': new_token,
    })


# ══════════════════════════════════════════════════════════════════════
# POST /api/auth/google  ← Google login button in login.html / signup.html
# Body: { email, name }
# ══════════════════════════════════════════════════════════════════════
@app.route('/api/auth/google', methods=['POST'])
def google_auth():
    data  = request.get_json(silent=True) or {}
    email = (data.get('email') or '').strip().lower()
    name  = (data.get('name')  or '').strip() or email.split('@')[0]

    if not email or '@' not in email:
        return jsonify({'error': 'Valid email is required.'}), 400

    db = get_db()
    user = db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()

    if user:
        # Existing user — just log them in
        new_token = generate_token()
        db.execute('UPDATE users SET token = ? WHERE id = ?', (new_token, user['id']))
        db.commit()
        return jsonify({
            'id': user['id'], 'name': user['name'],
            'email': user['email'], 'role': user['role'], 'token': new_token
        })
    else:
        # New user — register them
        token = generate_token()
        now   = datetime.utcnow().isoformat()
        cursor = db.execute(
            'INSERT INTO users (name, email, password, role, token, created_at) VALUES (?, ?, ?, ?, ?, ?)',
            (name, email, 'google-oauth', 'user', token, now)
        )
        db.commit()
        return jsonify({
            'id': cursor.lastrowid, 'name': name,
            'email': email, 'role': 'user', 'token': token
        }), 201


# ══════════════════════════════════════════════════════════════════════
# GET /api/users  ← (admin only) view all registered users
# ══════════════════════════════════════════════════════════════════════
@app.route('/api/users', methods=['GET'])
def get_users():
    """Returns all users (for admin/debugging — remove in production)"""
    db    = get_db()
    users = db.execute('SELECT id, name, email, role, created_at FROM users').fetchall()
    return jsonify([dict(u) for u in users])


# ══════════════════════════════════════════════════════════════════════
# GET /api/me  ← verify token, get current user info
# Header: Authorization: Bearer <token>
# ══════════════════════════════════════════════════════════════════════
@app.route('/api/me', methods=['GET'])
def get_me():
    """Verify the user's token and return their info"""
    auth  = request.headers.get('Authorization', '')
    token = auth.replace('Bearer ', '').strip()

    if not token:
        return jsonify({'error': 'No token provided. Please login.'}), 401

    db   = get_db()
    user = db.execute('SELECT * FROM users WHERE token = ?', (token,)).fetchone()

    if not user:
        return jsonify({'error': 'Invalid or expired token. Please login again.'}), 401

    return jsonify({
        'id':    user['id'],
        'name':  user['name'],
        'email': user['email'],
        'role':  user['role'],
    })


# ══════════════════════════════════════════════════════════════════════
# POST /api/lawyers  ← lawyer registration
# Body: { name, email, phone, district, legalArea, experienceYears, feeNpr, availability, languages, licenseNumber, specialization, bio, photo, document }
# ══════════════════════════════════════════════════════════════════════
@app.route('/api/lawyers', methods=['POST'])
def register_lawyer():
    """Register a new lawyer application"""
    auth  = request.headers.get('Authorization', '')
    token = auth.replace('Bearer ', '').strip()

    if not token:
        return jsonify({'error': 'Authentication required. Please login.'}), 401

    db = get_db()
    user = db.execute('SELECT * FROM users WHERE token = ?', (token,)).fetchone()

    if not user:
        return jsonify({'error': 'Invalid token. Please login again.'}), 401

    # Check if user already has a lawyer application
    existing = db.execute('SELECT id FROM lawyers WHERE user_id = ?', (user['id'],)).fetchone()
    if existing:
        return jsonify({'error': 'You already have a lawyer application pending.'}), 400

    data = request.get_json(silent=True) or {}

    name             = (data.get('name') or '').strip()
    email            = (data.get('email') or '').strip().lower()
    phone            = (data.get('phone') or '').strip()
    district         = (data.get('district') or '').strip()
    legal_area       = (data.get('legalArea') or '').strip()
    experience_years = data.get('experienceYears', 0)
    fee_npr          = data.get('feeNpr', 0)
    availability     = (data.get('availability') or '').strip()
    languages        = (data.get('languages') or '').strip()
    license_number   = (data.get('licenseNumber') or '').strip()
    specialization   = (data.get('specialization') or '').strip()
    bio              = (data.get('bio') or '').strip()
    photo            = (data.get('photo') or '').strip()
    document         = (data.get('document') or '').strip()

    # Validation
    if not all([name, email, phone, district, legal_area, license_number, specialization, bio]):
        return jsonify({'error': 'All required fields must be filled.'}), 400

    if experience_years < 0 or fee_npr < 0:
        return jsonify({'error': 'Experience years and fee must be positive numbers.'}), 400

    if legal_area not in ["Civil Law", "Family Law", "Criminal Law", "Property Law", "Labor Law", "Business Law", "Constitutional Law", "Land Rights"]:
        return jsonify({'error': 'Invalid legal area selected.'}), 400

    now = datetime.utcnow().isoformat()

    cursor = db.execute('''
        INSERT INTO lawyers (user_id, name, email, phone, district, legal_area, experience_years, fee_npr, availability, languages, license_number, specialization, bio, photo, document, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user['id'], name, email, phone, district, legal_area, experience_years, fee_npr, availability, languages, license_number, specialization, bio, photo, document, 'pending', now))

    db.commit()
    lawyer_id = cursor.lastrowid

    print(f"✅ Lawyer application submitted: {name} ({email})")

    return jsonify({
        'id': lawyer_id,
        'message': 'Lawyer application submitted successfully. Please wait for admin approval.',
        'status': 'pending'
    }), 201


# ══════════════════════════════════════════════════════════════════════
# GET /api/lawyers  ← get all approved lawyers
# Query params: ?area=...&district=...&q=...
# ══════════════════════════════════════════════════════════════════════
@app.route('/api/lawyers', methods=['GET'])
def get_lawyers():
    """Get all approved lawyers with optional filtering"""
    area = request.args.get('area', '').strip()
    district = request.args.get('district', '').strip()
    q = request.args.get('q', '').strip()

    db = get_db()
    query = '''
        SELECT l.*, u.name as user_name
        FROM lawyers l
        JOIN users u ON l.user_id = u.id
        WHERE l.status = 'approved'
    '''
    params = []

    if area and area != 'All':
        query += ' AND l.legal_area = ?'
        params.append(area)

    if district and district != 'All':
        query += ' AND l.district = ?'
        params.append(district)

    if q:
        query += ' AND (l.name LIKE ? OR l.specialization LIKE ? OR l.district LIKE ?)'
        search_term = f'%{q}%'
        params.extend([search_term, search_term, search_term])

    query += ' ORDER BY l.rating DESC, l.experience_years DESC'

    lawyers = db.execute(query, params).fetchall()

    return jsonify([{
        'id': l['id'],
        'name': l['name'],
        'email': l['email'],
        'phone': l['phone'],
        'district': l['district'],
        'legalArea': l['legal_area'],
        'experienceYears': l['experience_years'],
        'feeNpr': l['fee_npr'],
        'availability': l['availability'],
        'languages': l['languages'],
        'licenseNumber': l['license_number'],
        'specialization': l['specialization'],
        'bio': l['bio'],
        'photo': l['photo'],
        'rating': l['rating'] or 0.0,
        'status': l['status']
    } for l in lawyers])


# ══════════════════════════════════════════════════════════════════════
# GET /api/lawyers/<id>  ← get specific lawyer details
# ══════════════════════════════════════════════════════════════════════
@app.route('/api/lawyers/<int:lawyer_id>', methods=['GET'])
def get_lawyer(lawyer_id):
    """Get details of a specific lawyer"""
    db = get_db()
    lawyer = db.execute('''
        SELECT l.*, u.name as user_name
        FROM lawyers l
        JOIN users u ON l.user_id = u.id
        WHERE l.id = ? AND l.status = 'approved'
    ''', (lawyer_id,)).fetchone()

    if not lawyer:
        return jsonify({'error': 'Lawyer not found or not approved.'}), 404

    return jsonify({
        'id': lawyer['id'],
        'name': lawyer['name'],
        'email': lawyer['email'],
        'phone': lawyer['phone'],
        'district': lawyer['district'],
        'legalArea': lawyer['legal_area'],
        'experienceYears': lawyer['experience_years'],
        'feeNpr': lawyer['fee_npr'],
        'availability': lawyer['availability'],
        'languages': lawyer['languages'],
        'licenseNumber': lawyer['license_number'],
        'specialization': lawyer['specialization'],
        'bio': lawyer['bio'],
        'photo': lawyer['photo'],
        'rating': lawyer['rating'] or 0.0,
        'status': lawyer['status']
    })


# ══════════════════════════════════════════════════════════════════════
# GET /api/legal-areas  ← get all legal areas
# ══════════════════════════════════════════════════════════════════════
@app.route('/api/legal-areas', methods=['GET'])
def get_legal_areas():
    """Get all available legal areas"""
    areas = ["Civil Law", "Family Law", "Criminal Law", "Property Law", "Labor Law", "Business Law", "Constitutional Law", "Land Rights"]
    return jsonify(areas)


# ══════════════════════════════════════════════════════════════════════
# POST /api/appointments  ← book appointment
# Body: { lawyerId, date, time, mode, issueSummary, chatSummary }
# ══════════════════════════════════════════════════════════════════════
@app.route('/api/appointments', methods=['POST'])
def book_appointment():
    """Book an appointment with a lawyer"""
    auth  = request.headers.get('Authorization', '')
    token = auth.replace('Bearer ', '').strip()

    if not token:
        return jsonify({'error': 'Authentication required. Please login.'}), 401

    db = get_db()
    user = db.execute('SELECT * FROM users WHERE token = ?', (token,)).fetchone()

    if not user:
        return jsonify({'error': 'Invalid token. Please login again.'}), 401

    data = request.get_json(silent=True) or {}

    lawyer_id      = data.get('lawyerId')
    date           = (data.get('date') or '').strip()
    time           = (data.get('time') or '').strip()
    mode           = (data.get('mode') or '').strip()
    issue_summary  = (data.get('issueSummary') or '').strip()
    chat_summary   = (data.get('chatSummary') or '').strip()

    # Validation
    if not all([lawyer_id, date, time, mode, issue_summary]):
        return jsonify({'error': 'All required fields must be filled.'}), 400

    if mode not in ['Online', 'In-Person']:
        return jsonify({'error': 'Invalid appointment mode.'}), 400

    # Check if lawyer exists and is approved
    lawyer = db.execute('SELECT * FROM lawyers WHERE id = ? AND status = ?', (lawyer_id, 'approved')).fetchone()
    if not lawyer:
        return jsonify({'error': 'Lawyer not found or not approved.'}), 404

    # Check for conflicting appointments
    existing = db.execute('''
        SELECT id FROM appointments
        WHERE lawyer_id = ? AND date = ? AND time = ? AND status != 'cancelled'
    ''', (lawyer_id, date, time)).fetchone()

    if existing:
        return jsonify({'error': 'This time slot is already booked. Please choose a different time.'}), 400

    now = datetime.utcnow().isoformat()

    cursor = db.execute('''
        INSERT INTO appointments (user_id, lawyer_id, date, time, mode, issue_summary, chat_summary, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user['id'], lawyer_id, date, time, mode, issue_summary, chat_summary, 'pending', now))

    db.commit()
    appointment_id = cursor.lastrowid

    print(f"✅ Appointment booked: User {user['name']} with Lawyer {lawyer['name']} on {date} at {time}")

    return jsonify({
        'id': appointment_id,
        'message': 'Appointment booked successfully.',
        'status': 'pending'
    }), 201


# ══════════════════════════════════════════════════════════════════════
# GET /api/appointments  ← get user's appointments
# ══════════════════════════════════════════════════════════════════════
@app.route('/api/appointments', methods=['GET'])
def get_appointments():
    """Get current user's appointments"""
    auth  = request.headers.get('Authorization', '')
    token = auth.replace('Bearer ', '').strip()

    if not token:
        return jsonify({'error': 'Authentication required. Please login.'}), 401

    db = get_db()
    user = db.execute('SELECT * FROM users WHERE token = ?', (token,)).fetchone()

    if not user:
        return jsonify({'error': 'Invalid token. Please login again.'}), 401

    appointments = db.execute('''
        SELECT a.*, l.name as lawyer_name, l.email as lawyer_email, l.phone as lawyer_phone, l.legal_area, l.district
        FROM appointments a
        JOIN lawyers l ON a.lawyer_id = l.id
        WHERE a.user_id = ?
        ORDER BY a.date DESC, a.time DESC
    ''', (user['id'],)).fetchall()

    return jsonify([{
        'id': a['id'],
        'lawyerId': a['lawyer_id'],
        'lawyerName': a['lawyer_name'],
        'lawyerEmail': a['lawyer_email'],
        'lawyerPhone': a['lawyer_phone'],
        'legalArea': a['legal_area'],
        'district': a['district'],
        'date': a['date'],
        'time': a['time'],
        'mode': a['mode'],
        'issueSummary': a['issue_summary'],
        'chatSummary': a['chat_summary'],
        'status': a['status'],
        'createdAt': a['created_at']
    } for a in appointments])


# ══════════════════════════════════════════════════════════════════════
# PUT /api/appointments/<id>  ← update appointment status
# Body: { status }  (admin/lawyer only)
# ══════════════════════════════════════════════════════════════════════
@app.route('/api/appointments/<int:appointment_id>', methods=['PUT'])
def update_appointment_status(appointment_id):
    """Update appointment status (admin/lawyer only)"""
    auth  = request.headers.get('Authorization', '')
    token = auth.replace('Bearer ', '').strip()

    if not token:
        return jsonify({'error': 'Authentication required. Please login.'}), 401

    db = get_db()
    user = db.execute('SELECT * FROM users WHERE token = ?', (token,)).fetchone()

    if not user:
        return jsonify({'error': 'Invalid token. Please login again.'}), 401

    # Only admin and lawyers can update appointment status
    if user['role'] not in ['admin', 'lawyer']:
        return jsonify({'error': 'Only admins and lawyers can update appointment status.'}), 403

    data = request.get_json(silent=True) or {}
    new_status = (data.get('status') or '').strip()

    if new_status not in ['pending', 'confirmed', 'completed', 'cancelled']:
        return jsonify({'error': 'Invalid status. Must be: pending, confirmed, completed, or cancelled.'}), 400

    # If user is lawyer, check if they own this appointment
    if user['role'] == 'lawyer':
        lawyer = db.execute('SELECT id FROM lawyers WHERE user_id = ?', (user['id'],)).fetchone()
        if not lawyer:
            return jsonify({'error': 'Lawyer profile not found.'}), 404

        appointment = db.execute('''
            SELECT * FROM appointments WHERE id = ? AND lawyer_id = ?
        ''', (appointment_id, lawyer['id'])).fetchone()

        if not appointment:
            return jsonify({'error': 'Appointment not found or you do not have permission to update it.'}), 404
    else:
        # Admin can update any appointment
        appointment = db.execute('SELECT * FROM appointments WHERE id = ?', (appointment_id,)).fetchone()
        if not appointment:
            return jsonify({'error': 'Appointment not found.'}), 404

    db.execute('UPDATE appointments SET status = ? WHERE id = ?', (new_status, appointment_id))
    db.commit()

    print(f"✅ Appointment {appointment_id} status updated to: {new_status}")

    return jsonify({
        'message': f'Appointment status updated to {new_status}.',
        'status': new_status
    })


# ══════════════════════════════════════════════════════════════════════
# GET /api/admin/lawyers  ← admin: get all lawyer applications
# ══════════════════════════════════════════════════════════════════════
@app.route('/api/admin/lawyers', methods=['GET'])
def get_lawyer_applications():
    """Get all lawyer applications (admin only)"""
    auth  = request.headers.get('Authorization', '')
    token = auth.replace('Bearer ', '').strip()

    if not token:
        return jsonify({'error': 'Authentication required. Please login.'}), 401

    db = get_db()
    user = db.execute('SELECT * FROM users WHERE token = ?', (token,)).fetchone()

    if not user or user['role'] != 'admin':
        return jsonify({'error': 'Admin access required.'}), 403

    lawyers = db.execute('''
        SELECT l.*, u.name as user_name, u.email as user_email
        FROM lawyers l
        JOIN users u ON l.user_id = u.id
        ORDER BY l.created_at DESC
    ''').fetchall()

    return jsonify([{
        'id': l['id'],
        'userId': l['user_id'],
        'userName': l['user_name'],
        'userEmail': l['user_email'],
        'name': l['name'],
        'email': l['email'],
        'phone': l['phone'],
        'district': l['district'],
        'legalArea': l['legal_area'],
        'experienceYears': l['experience_years'],
        'feeNpr': l['fee_npr'],
        'availability': l['availability'],
        'languages': l['languages'],
        'licenseNumber': l['license_number'],
        'specialization': l['specialization'],
        'bio': l['bio'],
        'photo': l['photo'],
        'document': l['document'],
        'status': l['status'],
        'rating': l['rating'] or 0.0,
        'createdAt': l['created_at']
    } for l in lawyers])


# ══════════════════════════════════════════════════════════════════════
# PUT /api/admin/lawyers/<id>  ← admin: approve/reject lawyer
# Body: { status, rating }
# ══════════════════════════════════════════════════════════════════════
@app.route('/api/admin/lawyers/<int:lawyer_id>', methods=['PUT'])
def update_lawyer_status(lawyer_id):
    """Approve or reject lawyer application (admin only)"""
    auth  = request.headers.get('Authorization', '')
    token = auth.replace('Bearer ', '').strip()

    if not token:
        return jsonify({'error': 'Authentication required. Please login.'}), 401

    db = get_db()
    user = db.execute('SELECT * FROM users WHERE token = ?', (token,)).fetchone()

    if not user or user['role'] != 'admin':
        return jsonify({'error': 'Admin access required.'}), 403

    data = request.get_json(silent=True) or {}
    new_status = (data.get('status') or '').strip()
    rating = data.get('rating', 0.0)

    if new_status not in ['pending', 'approved', 'rejected']:
        return jsonify({'error': 'Invalid status. Must be: pending, approved, or rejected.'}), 400

    lawyer = db.execute('SELECT * FROM lawyers WHERE id = ?', (lawyer_id,)).fetchone()
    if not lawyer:
        return jsonify({'error': 'Lawyer application not found.'}), 404

    db.execute('UPDATE lawyers SET status = ?, rating = ? WHERE id = ?', (new_status, rating, lawyer_id))
    db.commit()

    print(f"✅ Lawyer {lawyer['name']} status updated to: {new_status}")

    return jsonify({
        'message': f'Lawyer application {new_status}.',
        'status': new_status
    })


# ══════════════════════════════════════════════════════════════════════
# Start server
# ══════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    init_db()
    print("\n🚀 KanoonSathi server running!")
    print("   Open: http://127.0.0.1:5000")
    print("   Signup: http://127.0.0.1:5000/signup.html")
    print("   Login:  http://127.0.0.1:5000/login.html\n")
    app.run(debug=True, port=5000)
