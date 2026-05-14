"""
Shared pytest fixtures for the Spendly test suite.

Architecture note: database/db.py resolves DB_PATH at import time as an
absolute filesystem path — there is no Flask config key that redirects the
connection.  Every db helper (get_db, init_db, seed_db, create_user, …)
calls get_db() internally, which calls sqlite3.connect(DB_PATH).

To isolate tests we patch `database.db.DB_PATH` to a per-session temp file
before any db call is made, then call init_db() + seed_db() against that
temp file.  Using ':memory:' would not work because each sqlite3.connect()
call on ':memory:' opens a *new*, empty database.
"""

import os
import tempfile
import pytest
import database.db as db_module
from app import app as flask_app
from database.db import init_db, seed_db


@pytest.fixture
def app(tmp_path):
    """
    Yield a Flask app wired to an isolated SQLite file under tmp_path.
    The file is unique per test invocation; pytest discards tmp_path
    automatically after the test.
    """
    db_file = str(tmp_path / "test_spendly.db")

    # Redirect every db.get_db() call to our temp file.
    original_db_path = db_module.DB_PATH
    db_module.DB_PATH = db_file

    flask_app.config.update(
        TESTING=True,
        SECRET_KEY="test-secret-key",
        WTF_CSRF_ENABLED=False,
    )

    # Populate schema + demo data against the patched path.
    init_db()
    seed_db()

    yield flask_app

    # Restore the original path so other test modules are not affected.
    db_module.DB_PATH = original_db_path


@pytest.fixture
def client(app):
    """Unauthenticated test client."""
    return app.test_client()


@pytest.fixture
def auth_client(client):
    """
    Test client that has already completed a successful login as the
    seeded demo user (demo@spendly.com / demo123).
    """
    client.post(
        "/login",
        data={"email": "demo@spendly.com", "password": "demo123"},
        follow_redirects=False,
    )
    return client
