import bcrypt
import hashlib
import secrets
import jwt
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status

SECRET_KEY  = "your-secret-key-change-in-production"   # move to .env
ALGORITHM   = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
RESET_TOKEN_EXPIRE_MINUTES  = 10   # OTP verified → 10 min to reset

# ─── Password ───
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())

# ─── Refresh Token ───
def generate_refresh_token() -> str:
    return secrets.token_urlsafe(64)

def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

# ─── OTP ───
def generate_otp() -> str:
    """6-digit numeric OTP"""
    return str(secrets.randbelow(900000) + 100000)   # 100000–999999

def hash_otp(otp: str) -> str:
    return bcrypt.hashpw(otp.encode(), bcrypt.gensalt(rounds=12)).decode()

def verify_otp(plain_otp: str, hashed_otp: str) -> bool:
    return bcrypt.checkpw(plain_otp.encode(), hashed_otp.encode())

# ─── JWT Access Token ───
def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"user_id": user_id, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Access token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ─── Short-lived Reset Token (after OTP verified) ───
def create_reset_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(
        {"user_id": user_id, "purpose": "password_reset", "exp": expire},
        SECRET_KEY, algorithm=ALGORITHM
    )

def decode_reset_token(token: str) -> int:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("purpose") != "password_reset":
            raise HTTPException(status_code=400, detail="Invalid reset token")
        return payload["user_id"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Reset token expired. Request a new OTP.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=400, detail="Invalid reset token")