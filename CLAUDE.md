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

- **`app.py`** — Flask application entry point. Registers all routes and configures the app instance. New routes go here; each route delegates to the database layer for data access.
- **`database/db.py`** — Database layer (SQLite via Python's `sqlite3`). Exposes `get_db()`, `init_db()`, and `seed_db()`. All SQL lives here — routes never construct queries directly.
- **`templates/`** — Jinja2 templates. `base.html` is the root layout that all other templates extend via `{% extends "base.html" %}`.
- **`static/css/style.css`** — All styling. Uses CSS custom properties (`--color-*`, `--radius-*`) defined at `:root`. The design system uses DM Serif Display for headings and DM Sans for body text, with a forest-green/warm-gold palette.

### Intended Route Structure

The app follows a standard CRUD pattern for expenses. Routes already stubbed in `app.py`:

| Route | Method | Purpose |
|---|---|---|
| `/` | GET | Landing page |
| `/register` | GET/POST | User registration |
| `/login` | GET/POST | User login |
| `/logout` | GET | Destroy session |
| `/profile` | GET | User profile |
| `/expenses/add` | GET/POST | Add expense |
| `/expenses/<id>/edit` | GET/POST | Edit expense |
| `/expenses/<id>/delete` | POST | Delete expense |

### Database

SQLite file is `expense_tracker.db` (gitignored). The schema and seed data are managed through `database/db.py`. Call `init_db()` to create tables and `seed_db()` to populate test data.

### Testing

Tests use `pytest-flask`. The test client is configured via a `conftest.py` fixture that creates an in-memory or temp SQLite database so tests never touch the real `expense_tracker.db`.
