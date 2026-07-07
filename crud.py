from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
import models, schemas
from auth import (
    hash_password, verify_password,
    hash_refresh_token, generate_refresh_token,
    generate_otp, hash_otp, verify_otp
)
from calculation import (
    calculate_age, calculate_bmi, calculate_bmr,
    calculate_tedd, calcutaed_calories_adjustment, get_body_type
)

# ═══════════════════════════════════════════════════
# USER
# ═══════════════════════════════════════════════════
def create_user(db: Session, user: schemas.usercreate):
    if get_user_by_email(db, user.email):
        raise HTTPException(status_code=409, detail="Email already registered")
    db_user = models.User(
        name     = user.name,
        email    = user.email.lower(),
        password = hash_password(user.password),
        is_admin = False
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(
        models.User.email == email.lower()
    ).first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


# ═══════════════════════════════════════════════════
# SESSION (Refresh Tokens)   — Remember Me support
# ═══════════════════════════════════════════════════
def create_session(db: Session, user_id: int, refresh_token: str, remember_me: bool):
    hashed = hash_refresh_token(refresh_token)
    # Remember Me → 30 days, else → 7 days
    days   = 30 if remember_me else 7
    expiry = datetime.now(timezone.utc) + timedelta(days=days)

    session_entry = models.token(
        user_id            = user_id,
        refresh_token_hash = hashed,
        is_remember_me     = remember_me,
        expires_at         = expiry
    )
    db.add(session_entry)
    db.commit()
    db.refresh(session_entry)
    return session_entry

def get_valid_session(db: Session, refresh_token: str):
    hashed = hash_refresh_token(refresh_token)
    entry  = db.query(models.token).filter(
        models.token.refresh_token_hash == hashed,
        models.token.revoked_at.is_(None)
    ).first()
    if not entry:
        return None
    if entry.expires_at < datetime.now(timezone.utc):
        return None
    return entry

def revoke_session(db: Session, refresh_token: str):
    hashed = hash_refresh_token(refresh_token)
    entry  = db.query(models.token).filter(
        models.token.refresh_token_hash == hashed
    ).first()
    if entry:
        entry.revoked_at = datetime.now(timezone.utc)
        db.commit()
    return entry

def revoke_all_sessions(db: Session, user_id: int):
    """Called after successful password reset — invalidates ALL sessions"""
    db.query(models.token).filter(
        models.token.user_id == user_id,
        models.token.revoked_at.is_(None)
    ).update({"revoked_at": datetime.now(timezone.utc)})
    db.commit()


# ═══════════════════════════════════════════════════
# FORGOT PASSWORD / OTP
# ═══════════════════════════════════════════════════
def create_otp(db: Session, user_id: int) -> str:
    """
    Generates OTP, stores hashed version, enforces 60-second resend cooldown.
    Returns plain OTP (to be emailed — never stored plain).
    """
    # 60-second resend cooldown
    cooldown_cutoff = datetime.now(timezone.utc) - timedelta(seconds=60)
    recent = db.query(models.PasswordResetOTP).filter(
        models.PasswordResetOTP.user_id    == user_id,
        models.PasswordResetOTP.created_at  >= cooldown_cutoff,
        models.PasswordResetOTP.consumed_at.is_(None)
    ).first()
    if recent:
        raise HTTPException(
            status_code=429,
            detail="Please wait 60 seconds before requesting another OTP"
        )

    plain_otp  = generate_otp()
    otp_entry  = models.PasswordResetOTP(
        user_id    = user_id,
        otp_hash   = hash_otp(plain_otp),
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)
    )
    db.add(otp_entry)
    db.commit()
    db.refresh(otp_entry)
    return plain_otp   # caller emails this

def verify_otp_and_get_user(db: Session, email: str, plain_otp: str) -> models.User:
    """
    Verifies OTP. Returns User on success.
    Increments attempt_count; rejects after 5 wrong attempts.
    """
    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get latest unconsumed, unexpired OTP
    otp_entry = db.query(models.PasswordResetOTP).filter(
        models.PasswordResetOTP.user_id     == user.id,
        models.PasswordResetOTP.consumed_at.is_(None),
        models.PasswordResetOTP.expires_at  >= datetime.now(timezone.utc)
    ).order_by(models.PasswordResetOTP.created_at.desc()).first()

    if not otp_entry:
        raise HTTPException(status_code=400, detail="OTP expired or not found. Request a new one.")

    if otp_entry.attempt_count >= 5:
        raise HTTPException(status_code=429, detail="Too many incorrect attempts. Request a new OTP.")

    if not verify_otp(plain_otp, otp_entry.otp_hash):
        otp_entry.attempt_count += 1
        db.commit()
        remaining = 5 - otp_entry.attempt_count
        raise HTTPException(
            status_code=400,
            detail=f"Incorrect OTP. {remaining} attempt(s) remaining."
        )

    # Mark as consumed
    otp_entry.consumed_at = datetime.now(timezone.utc)
    db.commit()
    return user

def reset_password(db: Session, user_id: int, new_password: str):
    """Updates password and revokes all active sessions."""
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.password = hash_password(new_password)
    db.commit()
    revoke_all_sessions(db, user_id)   # force logout everywhere


# ═══════════════════════════════════════════════════
# BODY PROFILE
# ═══════════════════════════════════════════════════
def create_body_profile(db: Session, user_id: int, data: schemas.Body_Profile_create):
    age         = calculate_age(data.DOB)
    bmi         = calculate_bmi(data.weight, data.height)
    body_type   = get_body_type(bmi)
    bmr         = calculate_bmr(data.weight, data.height, age, data.gender.value)
    tdee        = calculate_tedd(bmr, data.activity_level.value)
    calorie_adj = calcutaed_calories_adjustment(tdee, data.goal_type.value)

    profile = models.body_profile(
        user_id             = user_id,
        DOB                 = data.DOB,
        gender              = data.gender.value,
        height              = data.height,
        weight              = data.weight,
        activity_level      = data.activity_level.value,
        goal_type           = data.goal_type.value,
        target_weight       = data.target_weight,
        body_type           = body_type,
        bmi_value           = bmi,
        bmr                 = bmr,
        tdee                = tdee,
        calories_adjustment = calorie_adj,
        eating_pattern      = data.eating_pattern.value,
        recalculated_at     = datetime.now(timezone.utc)
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)

    # Mark onboarding complete
    user = get_user_by_id(db, user_id)
    if user:
        user.onboarding_completed = True
        db.commit()

    return profile
