from werkzeug.security import generate_password_hash, check_password_hash

# In-memory users — in production this would be a database table
USERS = {
    "superadmin": {
        "password": generate_password_hash("Admin@123"),
        "role": "super_admin",
        "display_name": "Super Admin",
    },
    "admin": {
        "password": generate_password_hash("Staff@123"),
        "role": "admin",
        "display_name": "Insurance Admin",
    },
}

def verify_user(username, password):
    user = USERS.get(username)
    if user and check_password_hash(user["password"], password):
        return {"username": username, "role": user["role"], "display_name": user["display_name"]}
    return None
