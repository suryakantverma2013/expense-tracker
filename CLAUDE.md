# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application (starts on http://localhost:5001)
python app.py

# Run all tests
pytest

# Run a single test file
pytest tests/test_auth.py

# Run a single test
pytest tests/test_auth.py::test_register_user
```

## Architecture

**Spendly** is a Flask personal expense tracker using SQLite, Jinja2 templates, and vanilla CSS/JS.

### Layers

- **`app.py`** — Flask entry point. Registers all routes; each route delegates to the database layer. Never constructs SQL directly here.
- **`database/db.py`** — All SQL lives here. Exposes `get_db()` (connection with `row_factory` and `PRAGMA foreign_keys = ON`), `init_db()` (CREATE TABLE IF NOT EXISTS), and `seed_db()` (demo data, idempotent). Use `werkzeug.security.generate_password_hash` / `check_password_hash` for passwords.
- **`templates/`** — Jinja2 templates. All pages extend `base.html` via `{% extends "base.html" %}` and override three blocks: `{% block title %}`, `{% block content %}`, `{% block scripts %}`.
- **`static/css/style.css`** — Global design system: CSS custom properties (`--ink`, `--paper`, `--accent` forest-green, `--accent-2` warm-gold, `--danger`) at `:root`. DM Serif Display for headings, DM Sans for body.
- **`static/css/landing.css`** — Landing-page-only styles (hero, dashboard mock, video modal). Only loaded by `landing.html`.

### Route Status

| Route | Method | Status |
|---|---|---|
| `/` | GET | Implemented |
| `/terms` | GET | Implemented |
| `/privacy` | GET | Implemented |
| `/register` | GET/POST | Template only — no backend logic yet |
| `/login` | GET/POST | Template only — no backend logic yet |
| `/logout` | GET | Stub |
| `/profile` | GET | Stub |
| `/expenses/add` | GET/POST | Stub |
| `/expenses/<id>/edit` | GET/POST | Stub |
| `/expenses/<id>/delete` | POST | Stub |

### Database Schema

- **users**: `id`, `name`, `email` (UNIQUE), `password_hash`, `created_at`
- **expenses**: `id`, `user_id` (FK → users), `amount` (REAL), `category` (Food/Transport/Bills/Health/Entertainment/Shopping/Other), `date` (YYYY-MM-DD), `description`, `created_at`

### Spec-Driven Workflow

Feature specs live in `.claude/specs/` as numbered markdown files (e.g. `01-database-setup.md`). Each spec defines the exact schema, function signatures, constraints, and a Definition of Done checklist. Always read the relevant spec before implementing a feature.

### Testing

Tests use `pytest-flask`. The `tests/` directory does not exist yet — create it with a `conftest.py` that provides a test client fixture using an in-memory or temp SQLite database so tests never touch `expense_tracker.db`.
