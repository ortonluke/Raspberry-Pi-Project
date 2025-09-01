import json

def load_users():
    with open("users.json", "r") as f:
        return json.load(f)

def save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f, indent=4)

def add_user(username):
    users = load_users()
    if username not in users:
        users[username] = {"XP":0, "wins":0, "skylanders":[]}
        save_users(users)

def valid_user(username):
    users = load_users()
    return username in users
