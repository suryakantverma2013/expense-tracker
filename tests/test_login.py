"""
tests/test_login.py
===================
Tests for Step 03: Login and Logout feature.

Routes under test
-----------------
  GET  /login   — render login form
  POST /login   — authenticate; set session or flash error
  GET  /logout  — clear session; redirect to /

Spec checklist
--------------
1.  GET /login renders form with email and password fields.
2.  Valid credentials → session["user_id"] set, redirect to /.
3.  Wrong password   → flash "Invalid email or password.", stay on login page.
4.  Unknown email    → same generic flash error, stay on login page.
5.  GET /logout      → clears session, redirects to /.
6.  After logout session["user_id"] is gone.
7.  /logout no longer returns a raw stub string.

Implementation note on flash rendering
---------------------------------------
app.py calls flash("Invalid email or password.", "error") then re-renders
login.html.  base.html renders flashes as:
    <div class="flash flash-error">{{ message }}</div>
The login template's own {{ error }} block is NOT populated by the current
implementation, so we assert against the flashed text, not the auth-error div.

Demo user (seeded by seed_db in conftest.py)
--------------------------------------------
  email    : demo@spendly.com
  password : demo123
"""

import pytest


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

DEMO_EMAIL = "demo@spendly.com"
DEMO_PASSWORD = "demo123"
INVALID_MESSAGE = b"Invalid email or password."


def _login(client, email=DEMO_EMAIL, password=DEMO_PASSWORD, follow=False):
    """POST /login with the given credentials."""
    return client.post(
        "/login",
        data={"email": email, "password": password},
        follow_redirects=follow,
    )


# ---------------------------------------------------------------------------
# Class: GET /login
# ---------------------------------------------------------------------------

class TestLoginPage:
    """GET /login renders the login form correctly."""

    def test_get_login_returns_200(self, client):
        response = client.get("/login")
        assert response.status_code == 200, (
            f"Expected 200 from GET /login, got {response.status_code}"
        )

    def test_get_login_contains_email_field(self, client):
        response = client.get("/login")
        assert b'name="email"' in response.data, (
            "Login form must contain an email input (name='email')"
        )

    def test_get_login_contains_password_field(self, client):
        response = client.get("/login")
        assert b'name="password"' in response.data, (
            "Login form must contain a password input (name='password')"
        )

    def test_get_login_contains_submit_button(self, client):
        response = client.get("/login")
        assert b"Sign in" in response.data, (
            "Login page must contain a 'Sign in' submit button"
        )

    def test_get_login_contains_page_title(self, client):
        response = client.get("/login")
        # The <title> block in login.html reads "Sign in — Spendly"
        assert b"Sign in" in response.data, (
            "Login page must include its expected title text"
        )

    def test_get_login_extends_base_template(self, client):
        response = client.get("/login")
        # base.html always renders the brand name in the navbar
        assert b"Spendly" in response.data, (
            "Login page must extend base.html (brand name must be present)"
        )


# ---------------------------------------------------------------------------
# Class: POST /login — happy path
# ---------------------------------------------------------------------------

class TestLoginSuccess:
    """Valid credentials produce a redirect and set session["user_id"]."""

    def test_valid_credentials_redirect_status(self, client):
        response = _login(client)
        assert response.status_code == 302, (
            f"Valid login must redirect (302), got {response.status_code}"
        )

    def test_valid_credentials_redirect_to_home(self, client):
        response = _login(client)
        location = response.headers.get("Location", "")
        assert location.endswith("/"), (
            f"Valid login must redirect to '/', got Location: {location}"
        )

    def test_valid_credentials_sets_session_user_id(self, client):
        """session['user_id'] must be populated after successful login."""
        with client.session_transaction() as pre_session:
            assert "user_id" not in pre_session, (
                "session must not contain user_id before login"
            )

        _login(client)

        with client.session_transaction() as post_session:
            assert "user_id" in post_session, (
                "session must contain 'user_id' after successful login"
            )

    def test_valid_credentials_session_user_id_is_integer(self, client):
        _login(client)
        with client.session_transaction() as sess:
            assert isinstance(sess["user_id"], int), (
                "session['user_id'] must be an integer (the user's PK)"
            )

    def test_following_redirect_lands_on_landing_page(self, client):
        response = _login(client, follow=True)
        assert response.status_code == 200, (
            "Following the post-login redirect must yield a 200"
        )
        # landing.html has the distinctive hero headline
        assert b"Track every rupee" in response.data or b"Spendly" in response.data, (
            "Redirect after login must land on the landing page"
        )


# ---------------------------------------------------------------------------
# Class: POST /login — failure paths
# ---------------------------------------------------------------------------

class TestLoginFailure:
    """Wrong or unknown credentials stay on the login page with an error."""

    def test_wrong_password_returns_200(self, client):
        response = _login(client, password="wrongpassword")
        assert response.status_code == 200, (
            f"Wrong password must re-render login (200), got {response.status_code}"
        )

    def test_wrong_password_shows_flash_error(self, client):
        response = _login(client, password="wrongpassword")
        assert INVALID_MESSAGE in response.data, (
            "Wrong password must flash 'Invalid email or password.'"
        )

    def test_wrong_password_does_not_set_session(self, client):
        _login(client, password="wrongpassword")
        with client.session_transaction() as sess:
            assert "user_id" not in sess, (
                "Failed login must not set session['user_id']"
            )

    def test_unknown_email_returns_200(self, client):
        response = _login(client, email="nobody@example.com")
        assert response.status_code == 200, (
            f"Unknown email must re-render login (200), got {response.status_code}"
        )

    def test_unknown_email_shows_flash_error(self, client):
        response = _login(client, email="nobody@example.com")
        assert INVALID_MESSAGE in response.data, (
            "Unknown email must flash 'Invalid email or password.' (generic message)"
        )

    def test_unknown_email_does_not_set_session(self, client):
        _login(client, email="nobody@example.com")
        with client.session_transaction() as sess:
            assert "user_id" not in sess, (
                "Failed login with unknown email must not set session['user_id']"
            )

    def test_empty_fields_returns_200(self, client):
        """Submitting the form with blank fields must not crash the server."""
        response = _login(client, email="", password="")
        assert response.status_code == 200, (
            f"Empty form POST to /login must return 200, got {response.status_code}"
        )

    def test_empty_fields_shows_flash_error(self, client):
        response = _login(client, email="", password="")
        assert INVALID_MESSAGE in response.data, (
            "Empty credentials must flash 'Invalid email or password.'"
        )

    def test_error_message_is_generic_not_revealing(self, client):
        """
        Both 'wrong password for known user' and 'unknown email' must
        produce the exact same error message — no user-enumeration hint.
        """
        wrong_pw_response = _login(client, password="bad")
        wrong_email_response = _login(client, email="ghost@nowhere.com")

        assert INVALID_MESSAGE in wrong_pw_response.data, (
            "Wrong password must show generic error"
        )
        assert INVALID_MESSAGE in wrong_email_response.data, (
            "Unknown email must show the same generic error"
        )


# ---------------------------------------------------------------------------
# Class: POST /login — parametrized edge cases
# ---------------------------------------------------------------------------

class TestLoginEdgeCases:
    """Parametrized checks for various bad-input scenarios."""

    @pytest.mark.parametrize("email, password", [
        ("", "demo123"),                          # missing email
        ("demo@spendly.com", ""),                 # missing password
        ("not-an-email", "demo123"),              # malformed email
        ("DEMO@SPENDLY.COM", "demo123"),          # wrong case (email is case-sensitive in DB)
        ("demo@spendly.com", "Demo123"),          # wrong password case
        ("'; DROP TABLE users; --", "x"),         # SQL injection attempt
    ])
    def test_bad_credentials_never_grant_access(self, client, email, password):
        """None of these inputs should result in a successful login."""
        _login(client, email=email, password=password)
        with client.session_transaction() as sess:
            assert "user_id" not in sess, (
                f"Credentials ({email!r}, {password!r}) must not grant access"
            )

    @pytest.mark.parametrize("email, password", [
        ("", "demo123"),
        ("demo@spendly.com", ""),
        ("not-an-email", "demo123"),
        ("'; DROP TABLE users; --", "x"),
    ])
    def test_bad_credentials_return_200(self, client, email, password):
        """Server must not crash (500) on malformed input."""
        response = _login(client, email=email, password=password)
        assert response.status_code == 200, (
            f"POST /login with ({email!r}, {password!r}) must return 200, "
            f"got {response.status_code}"
        )


# ---------------------------------------------------------------------------
# Class: GET /logout
# ---------------------------------------------------------------------------

class TestLogout:
    """GET /logout clears the session and redirects to /."""

    def test_logout_redirects_with_302(self, auth_client):
        response = auth_client.get("/logout")
        assert response.status_code == 302, (
            f"GET /logout must redirect (302), got {response.status_code}"
        )

    def test_logout_redirects_to_home(self, auth_client):
        response = auth_client.get("/logout")
        location = response.headers.get("Location", "")
        assert location.endswith("/"), (
            f"GET /logout must redirect to '/', got Location: {location}"
        )

    def test_logout_clears_session_user_id(self, auth_client):
        """session['user_id'] must be absent after logout."""
        # Confirm user_id is set before logout.
        with auth_client.session_transaction() as pre_sess:
            assert "user_id" in pre_sess, (
                "auth_client must have user_id in session before logout"
            )

        auth_client.get("/logout")

        with auth_client.session_transaction() as post_sess:
            assert "user_id" not in post_sess, (
                "session['user_id'] must be gone after logout"
            )

    def test_logout_clears_entire_session(self, auth_client):
        """session.clear() must leave the session empty, not just remove user_id."""
        auth_client.get("/logout")
        with auth_client.session_transaction() as sess:
            assert len(sess) == 0, (
                "Session must be completely empty after logout"
            )

    def test_logout_not_a_stub_string(self, auth_client):
        """Route must not return the old raw-text stub response."""
        response = auth_client.get("/logout")
        # A stub would be a 200 with plain text; we expect a 302 redirect.
        assert response.status_code != 200, (
            "/logout must not return a 200 plain-text stub; expected a redirect"
        )
        assert b"coming in" not in response.data, (
            "/logout must not contain stub placeholder text"
        )

    def test_logout_unauthenticated_still_redirects(self, client):
        """
        Calling /logout without being logged in must not crash.
        session.clear() on an already-empty session is a no-op, and the
        route should still redirect to /.
        """
        response = client.get("/logout")
        assert response.status_code == 302, (
            "Unauthenticated GET /logout must still redirect (302)"
        )

    def test_logout_following_redirect_shows_landing(self, auth_client):
        """After logout the landing page is served (not a login wall)."""
        response = auth_client.get("/logout", follow_redirects=True)
        assert response.status_code == 200, (
            "Following the logout redirect must yield a 200"
        )
        assert b"Spendly" in response.data, (
            "Landing page must be served after logout"
        )

    def test_login_after_logout_works(self, auth_client):
        """A user who logs out can log back in successfully."""
        auth_client.get("/logout")

        response = _login(auth_client, follow=False)
        assert response.status_code == 302, (
            "Re-login after logout must succeed with a 302 redirect"
        )
        with auth_client.session_transaction() as sess:
            assert "user_id" in sess, (
                "session['user_id'] must be set again after re-login"
            )
