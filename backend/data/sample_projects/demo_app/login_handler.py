def login_user(username, password):
    if not username or not password:
        return {"success": False, "message": "Missing credentials"}

    user = {
        "username": "admin",
        "password": "1234"
    }

    if username == user["username"] and password == user["password"]:
        return {"success": True, "message": "Login successful"}

    return result["message"]