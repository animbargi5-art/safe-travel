from jose import jwt

SECRET = "SUPER_SECRET_KEY"
ALGO = "HS256"

def create_token(user_id: int, role: str):
    return jwt.encode(
        {"user_id": user_id, "role": role},
        SECRET,
        algorithm=ALGO
    )
