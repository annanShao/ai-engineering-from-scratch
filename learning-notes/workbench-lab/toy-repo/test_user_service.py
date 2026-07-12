"""Authoritative tests. The agent must keep these green (and flip the
validation ones from red to green by implementing validation in the
ALLOWED file — never by editing this file).

- 2 happy-path tests: PASS_TO_PASS (must stay green).
- 3 validation tests: FAIL_TO_PASS (red until validation is implemented).
"""
import pytest
from user_service import create_user, get_user, users


def setup_function():
    users.clear()


# --- happy path: PASS_TO_PASS ---

def test_create_user_returns_record():
    rec = create_user("ava", 30, "ava@example.com")
    assert rec == {"age": 30, "email": "ava@example.com"}


def test_get_user_roundtrip():
    create_user("ben", 25, "ben@example.com")
    assert get_user("ben")["age"] == 25


# --- validation: FAIL_TO_PASS (red until create_user validates) ---

def test_rejects_empty_username():
    with pytest.raises(ValueError):
        create_user("", 30, "x@example.com")


def test_rejects_negative_age():
    with pytest.raises(ValueError):
        create_user("cara", -1, "cara@example.com")


def test_rejects_malformed_email():
    with pytest.raises(ValueError):
        create_user("dan", 40, "not-an-email")
