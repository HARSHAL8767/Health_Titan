from fastapi import APIRouter, Depends, HTTPException, Response, Cookie
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
import crud, schemas, auth
from db import get_db
from auth import generate_refresh_token

router  = APIRouter()
security = HTTPBearer()

# ── helper to get current user from JWT ──
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    payload = auth.decode_access_token(credentials.credentials)
    user    = crud.get_user_by_id(db, payload["user_id"])
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    if user.is_blocked:
        raise HTTPException(status_code=403, detail="Account blocked")
    return user


# ═══════════════════════════════════════════
# AUTH ROUTES
# ═══════════════════════════════════════════

@router.post("/auth/register", response_model=schemas.userresponse, status_code=201, tags=["Auth"])
def register(user: schemas.usercreate, db: Session = Depends(get_db)):
    return crud.create_user(db, user)


@router.post("/auth/login", response_model=schemas.loginresponse, tags=["Auth"])
def login(
    payload:  schemas.loginrequest,
    response: Response,
    db:       Session = Depends(get_db)
):
    user = crud.get_user_by_email(db, payload.email)
    if not user or not auth.verify_password(payload.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if user.is_blocked:
        raise HTTPException(status_code=403, detail="Account has been blocked")

    # Generate tokens
    access_token   = auth.create_access_token(user.id)
    refresh_token  = generate_refresh_token()
    crud.create_session(db, user.id, refresh_token, payload.remember_me)

    # Remember Me: 30 days cookie, else session cookie
    max_age = 30 * 24 * 3600 if payload.remember_me else None
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=max_age
    )

    return {"access_token": access_token, "token_type": "bearer", "message": "Login successful"}


@router.post("/auth/logout", tags=["Auth"])
def logout(
    response:      Response,
    refresh_token: Optional[str] = Cookie(default=None),
    db:            Session = Depends(get_db)
):
    if refresh_token:
        crud.revoke_session(db, refresh_token)
    response.delete_cookie("refresh_token")
    return {"message": "Logged out successfully"}


@router.post("/auth/refresh", tags=["Auth"])
def refresh_access_token(
    refresh_token: Optional[str] = Cookie(default=None),
    db:            Session = Depends(get_db)
):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token")
    session = crud.get_valid_session(db, refresh_token)
    if not session:
        raise HTTPException(status_code=401, detail="Session expired. Please login again.")
    access_token = auth.create_access_token(session.user_id)
    return {"access_token": access_token, "token_type": "bearer"}


# ═══════════════════════════════════════════
# FORGOT PASSWORD / RESET PASSWORD ROUTES
# ═══════════════════════════════════════════

@router.post("/auth/forgot-password",
             response_model=schemas.ForgotPasswordResponse,
             tags=["Password Reset"])
def forgot_password(
    payload: schemas.ForgotPasswordRequest,
    db:      Session = Depends(get_db)
):
    """
    Step 1 — User enters email.
    Always returns the same message to prevent email enumeration.
    OTP is generated and should be emailed (print for now).
    """
    user = crud.get_user_by_email(db, payload.email)
    if user:
        otp = crud.create_otp(db, user.id)
        # TODO: Replace print with actual email sending (e.g. SendGrid / SES)
        print(f"\n📧 OTP for {payload.email}: {otp}\n")

    return {"message": "If this email is registered, you will receive an OTP shortly."}


@router.post("/auth/verify-otp",
             response_model=schemas.VerifyOTPResponse,
             tags=["Password Reset"])
def verify_otp(
    payload: schemas.VerifyOTPRequest,
    db:      Session = Depends(get_db)
):
    """
    Step 2 — User submits OTP.
    Returns a short-lived reset_token (10 min) to authorize the actual reset.
    """
    user        = crud.verify_otp_and_get_user(db, payload.email, payload.otp)
    reset_token = auth.create_reset_token(user.id)
    return {
        "message":     "OTP verified. Use reset_token to set your new password.",
        "reset_token": reset_token
    }


@router.post("/auth/reset-password",
             response_model=schemas.ResetPasswordResponse,
             tags=["Password Reset"])
def reset_password(
    payload: schemas.ResetPasswordRequest,
    db:      Session = Depends(get_db)
):
    """
    Step 3 — User submits reset_token + new password.
    All active sessions are revoked after reset.
    """
    user_id = auth.decode_reset_token(payload.reset_token)
    crud.reset_password(db, user_id, payload.new_password)
    return {"message": "Password reset successfully. Please login with your new password."}


# ═══════════════════════════════════════════
# BODY PROFILE ROUTES
# ═══════════════════════════════════════════

@router.post("/onboarding/body-profile",
             response_model=schemas.Body_Profile_response,
             status_code=201,
             tags=["Onboarding"])
def create_body_profile(
    data:         schemas.Body_Profile_create,
    db:           Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return crud.create_body_profile(db, current_user.id, data)


@router.get("/onboarding/body-profile",
            response_model=schemas.Body_Profile_response,
            tags=["Onboarding"])
def get_body_profile(
    db:           Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    profile = current_user.body_profile
    if not profile:
        raise HTTPException(status_code=404, detail="Body profile not found. Please complete onboarding.")
    return profile