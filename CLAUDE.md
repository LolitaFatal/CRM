# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run the app (development, debug mode, port 5000)
python app.py

# Seed database with demo data (requires SUPABASE_SERVICE_KEY)
python -m backend.seed.seed_data

# Production server
gunicorn app:app
```

### Demo Credentials
- Doctor: `doctor@demo.com` / `demo1234`
- Secretary: `secretary@demo.com` / `demo1234`

## Architecture

### Stack
- **Backend**: Python Flask + Supabase (PostgreSQL)
- **Frontend**: Jinja2 templates + Tailwind CSS (CDN) + Chart.js + SortableJS
- **AI**: OpenAI API for RAG chat (NL→SQL), scikit-learn for churn prediction
- **Language**: Hebrew RTL (`dir="rtl"`, Heebo font)

### Request Flow
```
Route (Blueprint) → Service → Supabase client → PostgreSQL
```
- Routes handle HTTP, call services, return JSON or render templates
- Services contain business logic and Supabase queries
- `backend/extensions.py` provides the Supabase client singleton via `get_supabase()`

### Entry Point
`app.py` → `backend/__init__.py` (app factory) which sets `template_folder` and `static_folder` to `frontend/`.

### Blueprints (Routes)
All registered in `backend/routes/__init__.py`:
- `auth` - Login/logout, session management
- `dashboard` - KPIs, chart data APIs (`/api/dashboard/*-chart`)
- `patients` - CRUD + detail page with medical history
- `services` - Services catalog CRUD
- `appointments` - Appointments CRUD
- `invoices` - Invoices CRUD + mark-as-paid
- `tasks` - Kanban board CRUD + drag-drop status updates
- `chat` - RAG chat (doctor only)

### Auth & Authorization
- Session-based auth (Flask sessions with werkzeug password hashing)
- Decorators in `backend/middleware/auth_middleware.py`: `@login_required`, `@role_required(role)`
- **Secretary cannot access**: medical_history, chat, churn predictions (enforced by decorators + template conditionals)

### Database
- Schema defined in `backend/seed/schema.sql`
- Tables: `users`, `patients`, `medical_history`, `services`, `appointments`, `invoices`, `tasks`
- `medical_history` uses PostgreSQL `TEXT[]` arrays for diagnoses, medications, allergies
- `execute_readonly_query` RPC function required for RAG chat (defined in schema.sql)

### Frontend Patterns
- **Modal CRUD**: All entity pages use hidden modals opened via `openModal()`/`closeModal()` in `crud-tables.js`
- **AJAX**: All mutations go through `apiFetch()` in `utils.js` (fetch wrapper)
- **Pagination**: Server-side with `page`/`limit` params, offset calculation in services
- **Kanban**: SortableJS drag-drop → `PUT /api/tasks/<id>/status` with new status + position
- **Charts**: Chart.js fetching from `/api/dashboard/*-chart` endpoints, RTL-configured

### RAG Chat Pipeline
```
Hebrew question → GPT-4o (NL→SQL) → regex validation → Supabase RPC → GPT-4o-mini (results→Hebrew answer)
```
Security: regex blocks write operations; blocks access to `medical_history` and `password_hash` tables.

### Churn Prediction
Logistic Regression trained on-the-fly from patient activity features (days since last visit, cancelled ratio, etc.). Falls back to heuristic rules if insufficient data.

### API Response Format
All API endpoints return: `{"success": true/false, "data": ..., "error": "..."}` with pagination via `{"total", "page", "limit"}`.

## Design System
- Primary: `#197fe6`, Success: `#078838`, Warning: `#f59e0b`, Danger: `#e73908`
- Fonts: Heebo (Hebrew) + Manrope (Latin)
- Icons: Material Symbols Outlined
- Stitch UI prototypes in root folders are design references only (not used in app)

## Environment Variables
Required in `.env`: `FLASK_SECRET_KEY`, `SUPABASE_URL`, `SUPABASE_KEY`, `SUPABASE_SERVICE_KEY`, `OPENAI_API_KEY`
