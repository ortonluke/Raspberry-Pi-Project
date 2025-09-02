import json

USERS_FILE = "users.json"

def load_users():
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

def validate_user(username, pin):
    users = load_users()
    if username in users and users[username]["pin"] == pin:
        return True
    return False

def add_user(username, pin, skylander):
    users = load_users()
    if username in users:
        return False  # already exists
    users[username] = {"pin": pin, "skylander": skylander}
    save_users(users)
    return True
