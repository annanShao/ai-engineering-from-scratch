"""A deliberately under-validated user service.

This is the 'real repo' the agent works on across L32-L42.
The standing task: add input validation to create_user WITHOUT breaking
existing behavior and WITHOUT touching unrelated files.
"""

users = {}


def create_user(username, age, email):
    # No validation yet — this is the work to be done.
    users[username] = {"age": age, "email": email}
    return users[username]


def get_user(username):
    return users.get(username)
