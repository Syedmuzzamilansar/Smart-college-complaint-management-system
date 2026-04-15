# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  QQGPT — Smart College Complaint Management System                      ║
# ║  db_setup.py  ·  Database Initialisation & Schema Migration             ║
# ║  Run once after deployment, or any time the schema changes.             ║
# ║  Safe to re-run — all statements use CREATE TABLE IF NOT EXISTS.        ║
# ╚══════════════════════════════════════════════════════════════════════════╝
#
# Usage:
#   python db_setup.py
#
# What this script does (in order):
#   1. Connect to the PostgreSQL database defined in DATABASE_URL (.env)
#   2. Create all required tables if they do not already exist
#   3. Seed the admin account from ADMIN_EMAIL + ADMIN_PASSWORD_HASH
#   4. Prune expired password-reset tokens (safe maintenance step)
#   5. Print a status summary
#
# Tables managed:
#   users                  — student and admin accounts
#   complaints             — complaint records (named and anonymous)
#   password_reset_tokens  — time-limited tokens for self-service reset
#   login_attempts         — per-IP / per-email brute-force tracking
#   request_attempts       — per-endpoint rate-limit counters
# ──────────────────────────────────────────────────────────────────────────────

import os
import sys
from urllib.parse import urlparse
from types import SimpleNamespace

from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

try:
    import psycopg2
except Exception:
    import psycopg as _psycopg

    class _ConnectionProxy:
        def __init__(self, conn):
            self._conn = conn

        def __getattr__(self, name):
            return getattr(self._conn, name)

    psycopg2 = SimpleNamespace(
        connect=lambda *args, **kwargs: _ConnectionProxy(_psycopg.connect(*args, **kwargs)),
        OperationalError=_psycopg.OperationalError,
        IntegrityError=_psycopg.IntegrityError,
        Error=_psycopg.Error,
    )
load_dotenv()

# ── 1. Resolve and normalise DATABASE_URL ────────────────────────────────────
def _resolve_database_url():
    for key in (
        'DATABASE_URL',
        'POSTGRES_URL',
        'POSTGRESQL_URL',
        'RENDER_DATABASE_URL',
        'RENDER_POSTGRESQL_URL',
    ):
        value = (os.getenv(key) or '').strip()
        if value:
            return value
    return ''


DATABASE_URL = _resolve_database_url()
if not DATABASE_URL:
    print('[ERROR] Database URL is missing. Set DATABASE_URL (or POSTGRES_URL/POSTGRESQL_URL) and retry.')
    sys.exit(1)

db_url = DATABASE_URL
if db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql://', 1)
if 'sslmode=' not in db_url:
    sep    = '&' if '?' in db_url else '?'
    db_url = f'{db_url}{sep}sslmode=require'

host = urlparse(db_url).hostname or 'unknown'
print(f'[INFO] Connecting to database host: {host}')

# ── 2. Connect ────────────────────────────────────────────────────────────────
try:
    conn = psycopg2.connect(db_url, connect_timeout=12)
except psycopg2.OperationalError as exc:
    print(f'[ERROR] Cannot connect to {host}: {exc}')
    sys.exit(1)

conn.autocommit = False
c = conn.cursor()
print('[INFO] Connected successfully.')

# ── 3. Create tables ──────────────────────────────────────────────────────────

print('[INFO] Creating / verifying tables...')

# 3a. users
c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id         SERIAL PRIMARY KEY,
        name       TEXT NOT NULL,
        email      TEXT UNIQUE NOT NULL,
        password   TEXT NOT NULL,
        role       TEXT NOT NULL DEFAULT 'student',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
print('       [OK] users')

# 3b. complaints
c.execute('''
    CREATE TABLE IF NOT EXISTS complaints (
        id            SERIAL PRIMARY KEY,
        user_id       INTEGER,
        category      TEXT NOT NULL,
        description   TEXT NOT NULL,
        status        TEXT    DEFAULT 'Pending',
        priority      TEXT    DEFAULT 'Medium',
        assigned_to   TEXT,
        response      TEXT,
        is_anonymous  INTEGER DEFAULT 0,
        tracking_code TEXT,
        created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
''')
print('       [OK] complaints')

# 3c. password_reset_tokens  ← NEW in v5 (supports /forgot-password flow)
c.execute('''
    CREATE TABLE IF NOT EXISTS password_reset_tokens (
        id         SERIAL PRIMARY KEY,
        user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        token      TEXT    UNIQUE NOT NULL,
        expires_at TIMESTAMP NOT NULL,
        used       INTEGER NOT NULL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
print('       [OK] password_reset_tokens')

# 3d. login_attempts
c.execute('''
    CREATE TABLE IF NOT EXISTS login_attempts (
        key_type          TEXT NOT NULL,
        key_value         TEXT NOT NULL,
        attempt_count     INTEGER NOT NULL DEFAULT 0,
        window_started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        last_attempt_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (key_type, key_value)
    )
''')
print('       [OK] login_attempts')

# 3e. request_attempts
c.execute('''
    CREATE TABLE IF NOT EXISTS request_attempts (
        endpoint_name     TEXT NOT NULL,
        key_type          TEXT NOT NULL,
        key_value         TEXT NOT NULL,
        attempt_count     INTEGER NOT NULL DEFAULT 0,
        window_started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        last_attempt_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (endpoint_name, key_type, key_value)
    )
''')
print('       [OK] request_attempts')

# 3f. notices
c.execute('''
    CREATE TABLE IF NOT EXISTS notices (
        id         SERIAL PRIMARY KEY,
        title      TEXT NOT NULL,
        body       TEXT NOT NULL,
        posted_by  INTEGER REFERENCES users(id),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
print('       [OK] notices')

# 3g. complaint_feedback
c.execute('''
    CREATE TABLE IF NOT EXISTS complaint_feedback (
        id           SERIAL PRIMARY KEY,
        complaint_id INTEGER NOT NULL UNIQUE REFERENCES complaints(id) ON DELETE CASCADE,
        rating       INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
        comment      TEXT,
        created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
print('       [OK] complaint_feedback')

# Commit schema changes before attempting seed so a seed conflict cannot
# roll back the schema DDL.
conn.commit()
print('[INFO] Schema committed.')

# ── 4. Useful indexes (idempotent) ────────────────────────────────────────────
indexes = [
    ('idx_complaints_user_id',     'CREATE INDEX IF NOT EXISTS idx_complaints_user_id     ON complaints(user_id)'),
    ('idx_complaints_status',      'CREATE INDEX IF NOT EXISTS idx_complaints_status      ON complaints(status)'),
    ('idx_complaints_tracking',    'CREATE INDEX IF NOT EXISTS idx_complaints_tracking    ON complaints(tracking_code) WHERE is_anonymous = 1'),
    ('idx_prt_token',              'CREATE INDEX IF NOT EXISTS idx_prt_token              ON password_reset_tokens(token)'),
    ('idx_prt_user_id',            'CREATE INDEX IF NOT EXISTS idx_prt_user_id            ON password_reset_tokens(user_id)'),
    ('idx_notices_created_at',     'CREATE INDEX IF NOT EXISTS idx_notices_created_at     ON notices(created_at DESC)'),
    ('idx_feedback_complaint_id',  'CREATE INDEX IF NOT EXISTS idx_feedback_complaint_id  ON complaint_feedback(complaint_id)'),
]
print('[INFO] Creating / verifying indexes...')
for name, sql in indexes:
    c.execute(sql)
    print(f'       [OK] {name}')
conn.commit()

# ── 5. Seed admin account ─────────────────────────────────────────────────────
admin_email    = os.getenv('ADMIN_EMAIL', '').strip().lower()
admin_pw_hash  = os.getenv('ADMIN_PASSWORD_HASH', '').strip()
admin_pw_plain = os.getenv('ADMIN_PASSWORD', '').strip()

if not admin_email:
    print('[WARN] Admin seed skipped — ADMIN_EMAIL is not set.')
else:
    if not admin_pw_hash and admin_pw_plain:
        admin_pw_hash = generate_password_hash(admin_pw_plain)
        print('[INFO] Hashed ADMIN_PASSWORD for seed.')

    if not admin_pw_hash:
        print('[WARN] Admin seed skipped — neither ADMIN_PASSWORD_HASH nor ADMIN_PASSWORD is set.')
    else:
        c.execute("SELECT 1 FROM users WHERE role = 'admin' LIMIT 1")
        if c.fetchone():
            print('[INFO] Admin account already exists — seed skipped.')
        else:
            try:
                c.execute(
                    "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, 'admin')",
                    ('Admin', admin_email, admin_pw_hash),
                )
                conn.commit()
                print(f'[INFO] Admin account created: {admin_email}')
            except psycopg2.IntegrityError:
                conn.rollback()
                print(f'[INFO] Email {admin_email} already registered — admin seed skipped.')

# ── 6. Prune expired password-reset tokens ────────────────────────────────────
c.execute("DELETE FROM password_reset_tokens WHERE expires_at < NOW() OR used = 1")
pruned = c.rowcount
conn.commit()
if pruned:
    print(f'[INFO] Pruned {pruned} expired/used password-reset token(s).')

# ── 7. Summary ────────────────────────────────────────────────────────────────
c.execute("SELECT COUNT(*) FROM users WHERE role = 'student'")
student_row = c.fetchone() or (0,)
student_count = student_row[0]
c.execute("SELECT COUNT(*) FROM complaints")
complaint_row = c.fetchone() or (0,)
complaint_count = complaint_row[0]
c.execute("SELECT COUNT(*) FROM complaints WHERE status = 'Pending'")
pending_row = c.fetchone() or (0,)
pending_count = pending_row[0]

print()
print('┌─────────────────────────────────────────────┐')
print('│  QQGPT — Database Initialisation Complete   │')
print('├─────────────────────────────────────────────┤')
print(f'│  Students registered : {student_count:<22}│')
print(f'│  Total complaints    : {complaint_count:<22}│')
print(f'│  Pending complaints  : {pending_count:<22}│')
print('└─────────────────────────────────────────────┘')

c.close()
conn.close()
