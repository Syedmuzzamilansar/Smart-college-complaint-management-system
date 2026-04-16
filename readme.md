# QQGPT — Smart College Complaint Management System

> A production-ready web application for digitising and streamlining the complaint management process at Quli Qutub Shah Government Polytechnic, Hyderabad. Built with Flask, PostgreSQL, and powered by Google Gemini AI.

---

## Table of Contents

- [Overview](#overview)
- [Live Demo](#live-demo)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started (Local)](#getting-started-local)
- [Environment Variables](#environment-variables)
- [Database Setup](#database-setup)
- [Deployment on Render](#deployment-on-render)
- [Portal Pages & Routes](#portal-pages--routes)
- [User Roles](#user-roles)
- [Complaint Workflow](#complaint-workflow)
- [AI Chatbot (QQGPT Live Assistant)](#ai-chatbot-qqgpt-live-assistant)
- [Security Features](#security-features)
- [Health Check & Utilities](#health-check--utilities)
- [Contributing](#contributing)
- [Institution](#institution)

---

## Overview

The Smart Complaint Management System (Smart CMS) is a full-stack web application that allows students at Quli Qutub Shah Government Polytechnic to submit, track, and follow up on complaints about campus facilities — such as classrooms, laboratories, washrooms, libraries, and more. Administrators can review, prioritise, assign, and resolve complaints through a dedicated admin dashboard. The system also supports **anonymous complaint submission** with a tracking code, so students can raise concerns without revealing their identity.

At the heart of the portal is **QQGPT Live Assistant**, a Gemini-powered AI chatbot that acts as a live website copilot — guiding users through registration, complaint filing, password recovery, and general college queries in real time.

---

## Live Demo

The application is deployed on Render and is accessible at:

```
https://smart-college-complaint-management-system.onrender.com
```

> Note: The app is hosted on Render's free tier. The first load after inactivity may take 30–60 seconds as the service wakes up. This is normal behaviour for free-tier deployments.

---

## Features

### Student Features
- Account registration and login with secure password hashing
- Submit complaints under predefined categories with priority levels
- Edit pending complaints before admin review
- View complaint history and real-time status updates on the dashboard
- Submit anonymous complaints without an account — receive a 12-character tracking code
- Track anonymous complaint status at any time using the tracking code
- Self-service password reset via the Forgot Password flow (no email server required)
- Rate and comment on resolved complaints as feedback
- Browse college notices posted by admin

### Admin Features
- Dedicated admin dashboard showing all complaints with filters and sorting
- Update complaint status: Pending → In-Progress → Resolved / Rejected
- Assign complaints to staff and add admin responses
- Post and delete college notices visible to all users
- View and manage complaint feedback and public feedback
- Export all complaint data as a CSV file
- Permanently delete complaints

### AI Chatbot — QQGPT Live Assistant
- Powered by Google Gemini (`gemini-2.0-flash`)
- Native multi-turn conversation with full context retention
- Guided complaint drafting: collects category, location, and description step-by-step
- Portal navigation assistance with direct URL references
- College information Q&A (admissions, departments, contact, results)
- Context-aware suggestion chips per conversation stage
- Typing indicator support for frontend integration
- Rate limited to prevent abuse

### Security & Reliability
- CSRF token protection on all POST forms
- Per-IP and per-email brute-force login protection with time-windowed rate limiting
- Per-endpoint rate limiting (register, anonymous submit, chatbot API, etc.)
- Session-based authentication with role separation (student / admin)
- Passwords stored as Werkzeug-generated secure hashes — never in plain text
- PostgreSQL connection with SSL enforced
- Auto-retry database connection with exponential backoff (handles cold starts)

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12, Flask 3.0.3 |
| Database | PostgreSQL (via Supabase) |
| DB Driver | psycopg3 (`psycopg[binary]`) |
| AI / Chatbot | Google Gemini API (`gemini-2.0-flash`) |
| Authentication | Werkzeug password hashing, Flask sessions |
| Frontend | Jinja2 templates, HTML5, CSS3, JavaScript |
| Production Server | Gunicorn 22.0.0 |
| Deployment | Render (Web Service) |
| Environment | python-dotenv |

---

## Project Structure

```
smart-cms/
│
├── app.py                  # Main Flask application — all routes, logic, AI layer
├── db_setup.py             # Database initialisation & schema migration script
├── main.py                 # Health check + development launch utility
├── requirements.txt        # Python dependencies
├── runtime.txt             # Python version for Render
├── .python-version         # Python version for local environments
├── Procfile                # Gunicorn start command for Render
├── env_template.txt        # Template for creating your .env file
│
├── templates/              # Jinja2 HTML templates
│   ├── homepage.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── admin_dashboard.html
│   ├── admin_login.html
│   ├── admin_notices.html
│   ├── admin_feedback.html
│   ├── anonymous.html
│   ├── track.html
│   ├── notices.html
│   ├── forgot_password.html
│   ├── reset_password.html
│   ├── public_feedback.html
│   └── error.html
│
└── static/                 # Static assets (CSS, JS, images)
    └── images/
        └── qqsgpt-logo.svg
```

---

## Getting Started (Local)

### Prerequisites

Make sure you have the following installed on your machine:
- Python 3.12 or higher
- Git
- A PostgreSQL database (Supabase free tier is recommended)
- A Google Gemini API key (free at [aistudio.google.com](https://aistudio.google.com))

### Step 1 — Clone the repository

```bash
git clone https://github.com/Syedmuzzamilansar/Smart-college-complaint-management-system.git
cd Smart-college-complaint-management-system
```

### Step 2 — Create and activate a virtual environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Set up environment variables

Copy the template and fill in your values:

```bash
# Rename env_template.txt to .env
# Then edit .env with your actual credentials
```

See the [Environment Variables](#environment-variables) section for a full explanation of each variable.

### Step 5 — Initialise the database

```bash
python db_setup.py
```

This creates all required tables, indexes, and seeds the admin account. It is safe to re-run at any time.

### Step 6 — Run the application

```bash
# Full health check + launch (recommended for first run)
python main.py

# Or launch directly
python main.py --serve

# Or with Gunicorn (production-style)
gunicorn -w 2 -b 0.0.0.0:5001 app:app
```

The app will be available at `http://127.0.0.1:5001`.

---

## Environment Variables

Create a `.env` file in the project root (use `env_template.txt` as a guide). The following variables are required:

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | Full PostgreSQL connection string (use the **Transaction Pooler** URL from Supabase for IPv4 compatibility) | Yes |
| `SECRET_KEY` | A long random string used to sign Flask sessions (min 16 characters) | Yes |
| `ADMIN_EMAIL` | Email address for the admin account | Yes |
| `ADMIN_PASSWORD_HASH` | Werkzeug-hashed password for the admin account | Yes |
| `GEMINI_API_KEY` | Google Gemini API key for the AI chatbot | Yes |
| `GEMINI_MODEL` | Gemini model name (default: `gemini-2.0-flash`) | No |
| `FLASK_ENV` | Set to `production` on Render | No |
| `FLASK_DEBUG` | Set to `0` in production | No |

> **Important:** Never commit your `.env` file to version control. It is listed in `.gitignore` by default.

To generate an `ADMIN_PASSWORD_HASH`, run this in Python:

```python
from werkzeug.security import generate_password_hash
print(generate_password_hash("YourAdminPassword"))
```

Paste the output into `ADMIN_PASSWORD_HASH` in your `.env` file and on Render.

---

## Database Setup

The project uses PostgreSQL. The recommended free hosting provider is **Supabase**.

### Setting up Supabase

1. Go to [supabase.com](https://supabase.com) and create a free project.
2. Go to **Settings → Database** and reset/set your database password.
3. Click the green **Connect** button at the top of the page.
4. Select the **Transaction pooler** option (this is IPv4 compatible — required for Render's free tier).
5. Copy the connection URI and replace `[YOUR-PASSWORD]` with your actual password.
6. Set this as your `DATABASE_URL` environment variable.

### Running the schema migration

After setting `DATABASE_URL`, run:

```bash
python db_setup.py
```

This script will:
- Create all 7 tables: `users`, `complaints`, `password_reset_tokens`, `login_attempts`, `request_attempts`, `notices`, `complaint_feedback`
- Create 7 performance indexes
- Seed the admin account from your environment variables
- Prune expired password reset tokens
- Print a summary of current database state

The script is idempotent — running it multiple times will not duplicate data or break anything.

---

## Deployment on Render

### Step 1 — Push your code to GitHub

Make sure your repository is up to date:

```bash
git add .
git commit -m "your commit message"
git push origin main
```

### Step 2 — Create a new Web Service on Render

1. Log in to [render.com](https://render.com) and click **New → Web Service**.
2. Connect your GitHub repository.
3. Set the **Build Command** to: `pip install -r requirements.txt`
4. Set the **Start Command** to: `gunicorn app:app`

### Step 3 — Add environment variables

In your Render service, go to the **Environment** tab and add all variables listed in the [Environment Variables](#environment-variables) section.

### Step 4 — Deploy

Click **Create Web Service**. Render will build and deploy automatically. Subsequent pushes to the `main` branch will trigger automatic redeployments.

### Step 5 — Initialise the database

After the first successful deploy, run `db_setup.py` locally (with the same `DATABASE_URL` set in your `.env`) to create the schema in your production database.

### Keeping the service awake

Render's free tier puts services to sleep after 15 minutes of inactivity. To prevent cold-start delays for users, set up a free uptime monitor at [uptimerobot.com](https://uptimerobot.com) that pings your service every 5 minutes.

---

## Portal Pages & Routes

| Route | Method | Description | Access |
|-------|--------|-------------|--------|
| `/` | GET | Homepage | Public |
| `/register` | GET, POST | Student registration | Public |
| `/login` | GET, POST | Student and admin login | Public |
| `/admin-login` | GET | Admin login redirect page | Public |
| `/logout` | GET | End session | Authenticated |
| `/dashboard` | GET | Student complaint dashboard | Student |
| `/submit` | GET, POST | Submit a new complaint | Student |
| `/edit/<id>` | GET, POST | Edit a pending complaint | Student (owner) |
| `/delete/<id>` | POST | Delete a complaint | Student (owner) |
| `/anonymous` | GET, POST | Submit anonymous complaint | Public |
| `/track` | GET, POST | Track anonymous complaint | Public |
| `/forgot-password` | GET, POST | Self-service password reset | Public |
| `/notices` | GET | View college notices | Public |
| `/feedback/<id>` | GET, POST | Rate a resolved complaint | Student |
| `/feedback-public` | GET, POST | Submit general feedback | Public |
| `/admin/dashboard` | GET | Admin complaint management | Admin |
| `/admin/notices` | GET, POST | Post and manage notices | Admin |
| `/admin/feedback` | GET | View all feedback | Admin |
| `/admin/export` | GET | Export complaints as CSV | Admin |
| `/update_status/<id>` | POST | Change complaint status | Admin |
| `/admin/reject/<id>` | POST | Reject a complaint | Admin |
| `/admin/delete/<id>` | POST | Delete a complaint | Admin |
| `/api/chatbot` | POST | AI chatbot endpoint | Public |
| `/api/complaint-suggest` | POST | AI complaint suggestion | Student |

---

## User Roles

The system has two roles — **student** and **admin**. Both share the same `/login` page; role-based redirection happens automatically after authentication.

**Students** can register, submit complaints (named or anonymous), track complaint status, edit pending complaints, and submit feedback on resolved complaints.

**Admins** are seeded via `db_setup.py` and cannot register through the portal. Admins have full access to the admin dashboard, can manage all complaints, post notices, and export data. Admin routes are protected by the `@admin_required` decorator which returns a 403 if accessed by a non-admin session.

---

## Complaint Workflow

A complaint moves through the following lifecycle:

```
Student Submits → [Pending] → Admin Reviews → [In-Progress] → Admin Resolves → [Resolved]
                                           ↘ Admin Rejects → [Rejected]
```

Students can edit their complaint only while it remains in **Pending** status. Once the admin moves it to **In-Progress** or beyond, the complaint is locked for editing. For anonymous complaints, the tracking code displayed after submission is the only way to check status — it cannot be recovered if lost.

**Complaint categories:** Classroom, Computer Laboratory, Men Washroom, Women Washroom, Drinking Water, Library, Sports Facility, Other.

**Priority levels:** Low, Medium, High.

---

## AI Chatbot (QQGPT Live Assistant)

The chatbot is integrated directly into the homepage and runs on the `/api/chatbot` endpoint. It uses the **Google Gemini API** with a native multi-turn `contents[]` format for accurate, context-aware conversations.

### What the chatbot can do

The chatbot operates as a **live website copilot** with four core capabilities:

**Complaint Assistance** — It guides students through filing a complaint step by step, collecting complainant type, branch, year, PIN, category, location (including hall/room number for classroom issues), and description. It then produces a ready-to-paste complaint draft and directs the user to `/submit` or `/anonymous`.

**Portal Navigation** — It explains how to register, log in, reset passwords, track complaints, and use the dashboard. It references actual page routes in its responses.

**College Information** — It answers questions about QQGPT's departments, admission process (POLYCET), SBTET exam results, fees, timetables, holidays, and contact details. Time-sensitive queries are advised to be verified on official sources.

**General Conversation** — It responds warmly to greetings and introductions, and redirects off-topic questions back to relevant portal functionality.

### Technical notes

- Uses `gemini-2.0-flash` by default (configurable via `GEMINI_MODEL`)
- Long conversation histories are compressed with a rolling summary to preserve context
- Safety settings are tuned to avoid false positives on college-related terms like "marks", "attendance", and "exams"
- Rate limited to 30 requests per 60 seconds per IP
- The chatbot never takes actions on behalf of users — it only guides

---

## Security Features

**CSRF Protection** — Every POST form includes a CSRF token generated per session. All incoming POST requests are validated against the stored token before processing.

**Brute-force Protection** — Login attempts are tracked per IP address and per email address. Repeated failures trigger a rate-limit window that blocks further attempts temporarily.

**Rate Limiting** — Individual endpoints have configurable limits. For example, registration is limited to 6 requests per 60 seconds, anonymous submissions to 10 per 60 seconds, and the chatbot API to 30 per 60 seconds.

**Password Security** — All passwords are hashed using Werkzeug's `generate_password_hash` (PBKDF2-HMAC-SHA256). Plain-text passwords are never stored or logged.

**Session Security** — Sessions are signed with `SECRET_KEY`. Role and user identity are stored server-side and checked on every protected route.

**Database Security** — All connections use `sslmode=require`. The application uses parameterised queries throughout to prevent SQL injection.

---

## Health Check & Utilities

### `main.py` — Pre-flight health check

Run `python main.py --check` before deploying or after any configuration change. It verifies that all required environment variables are set, that the database is reachable, that the Gemini API key is present and valid, and that the `SECRET_KEY` meets minimum strength requirements. It exits with code `0` on success and `1` on failure.

```bash
python main.py            # Health check + launch Flask dev server
python main.py --check    # Health check only
python main.py --serve    # Skip check, launch Flask directly
```

### `db_setup.py` — Schema migration

Safe to re-run at any time. Uses `CREATE TABLE IF NOT EXISTS` and `CREATE INDEX IF NOT EXISTS` throughout. Also prunes expired password reset tokens as a maintenance step.

---

## Contributing

This project was built as a final year CSE project at QQGPT. If you would like to contribute improvements or report issues, please open a GitHub issue or pull request.

---

## Institution

**Quli Qutub Shah Government Polytechnic (QQGPT)**
Chaitanyapuri, Dilsukhnagar, Hyderabad 500060, Telangana, India
Affiliated to SBTET Telangana | NBA Accredited | Est. 1985

- Phone: 040-24040971
- Email: qqgpthyd@gmail.com
- Website: [qqgpthyd.dte.telangana.gov.in](http://qqgpthyd.dte.telangana.gov.in)

**Departments:** CSE · ECE · EEE · Mechanical Engineering · Civil Engineering · AI & DS · Commercial Practice

---

**Project by:** 23061-CS-012, 033, 039, 046, 064
**Guided by:** Ms. G Varshini, CSE Department
**Academic Year:** 2025–2026
