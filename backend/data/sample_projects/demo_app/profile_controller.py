def update_profile(data):
    if data is None:
        raise ValueError("Profile data cannot be None")

    username = data["username"]
    email = data["email"]

    if "@" not in email:
        raise ValueError("Invalid email")

    updated_profile = {
        "username": username,
        "email": email,
        "bio": data.get("bio", "")
    }

    return updated_profile


def save_profile(data):
    profile = update_profile(data)

    # simulated bug
    return profile["non_existing_key"]