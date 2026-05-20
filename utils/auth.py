"""
streamlit-authenticator 0.4.x glue.

We build the credentials dict from st.secrets so no plaintext YAML
exists on disk in the repo. Expected secrets layout:

  [auth]
  cookie_name = "wfm_scheduler_auth"
  cookie_key  = "change-me-32+chars-of-randomness"
  expiry_days = 1

  [auth.credentials.jsmith]
  email    = "jsmith@ap.com"
  name     = "John Smith"
  password = "$2b$12$...bcrypt-hash..."
  roles    = ["admin"]
"""
from __future__ import annotations
import streamlit as st
import streamlit_authenticator as stauth


def _credentials_from_secrets() -> dict:
    """Build the stauth credentials dict from st.secrets blocks."""
    auth = st.secrets["auth"]
    users = {}
    for username, blob in auth["credentials"].items():
        users[username] = {
            "email": blob["email"],
            "name": blob["name"],
            "password": blob["password"],
            "roles": list(blob.get("roles", ["viewer"])),
            "failed_login_attempts": 0,
            "logged_in": False,
        }
    return {"usernames": users}


def build_authenticator() -> stauth.Authenticate:
    """Construct the Authenticate object once per session."""
    auth = st.secrets["auth"]
    return stauth.Authenticate(
        credentials=_credentials_from_secrets(),
        cookie_name=auth["cookie_name"],
        cookie_key=auth["cookie_key"],
        cookie_expiry_days=float(auth.get("expiry_days", 1)),
        auto_hash=False,   # passwords in secrets are pre-bcrypt-hashed
    )


def is_authenticated() -> bool:
    """True iff the current session has logged in successfully."""
    return bool(st.session_state.get("authentication_status"))


def current_user() -> dict:
    """Convenience accessor for the logged-in user's profile."""
    return {
        "username": st.session_state.get("username"),
        "name":     st.session_state.get("name"),
        "roles":    st.session_state.get("roles", []) or [],
    }


def require_role(role: str) -> None:
    """Page-level gate. Call at the top of a sensitive page; halts on miss."""
    if role not in (st.session_state.get("roles") or []):
        st.error(f"🚫 Access denied. This page requires the **{role}** role.")
        st.stop()
