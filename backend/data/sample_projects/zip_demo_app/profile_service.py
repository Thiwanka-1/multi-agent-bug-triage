def build_profile(name, email):
    return {
        "name": name,
        "email": email,
        "role": "user"
    }


def get_profile_name(profile):
    return profile["full_name"]