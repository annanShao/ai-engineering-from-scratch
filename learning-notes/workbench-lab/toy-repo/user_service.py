"""A user service with input validation on create_user.

Task T1 (done via the workbench): reject empty username, negative age, and
malformed email, without changing the happy-path behavior.
"""
import re

users = {}

_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def create_user(username, age, email):
    if not username:
        raise ValueError("username must be non-empty")
    if age < 0:
        raise ValueError("age must be non-negative")
    if not _EMAIL.match(email):
        raise ValueError("email is malformed")
    users[username] = {"age": age, "email": email}
    return users[username]


def get_user(username):
    return users.get(username)
