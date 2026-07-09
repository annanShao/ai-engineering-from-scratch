"""Authoritative tests. The agent must keep these green.

The happy-path tests already pass. The validation tests are xfail-marked
placeholders: the standing task is to implement validation and flip them
to passing WITHOUT breaking the happy path.
"""
import pytest
from user_service import create_user, get_user, users


def setup_function():
    users.clear()


# --- happy path: must stay green (PASS_TO_PASS) ---

def test_create_user_returns_record():
    rec = create_user("ava", 30, "ava@example.com")
    assert rec == {"age": 30, "email": "ava@example.com"}


def test_get_user_roundtrip():
    create_user("ben", 25, "ben@example.com")
    assert get_user("ben")["age"] == 25


# --- validation: currently failing, the work is to make these pass (FAIL_TO_PASS) ---

@pytest.mark.xfail(reason="validation not implemented yet", strict=True)
def test_rejects_empty_username():
    with pytest.raises(ValueError):
        create_user("", 30, "x@example.com")


@pytest.mark.xfail(reason="validation not implemented yet", strict=True)
def test_rejects_negative_age():
    with pytest.raises(ValueError):
        create_user("cara", -1, "cara@example.com")


@pytest.mark.xfail(reason="validation not implemented yet", strict=True)
def test_rejects_malformed_email():
    with pytest.raises(ValueError):
        create_user("dan", 40, "not-an-email")
