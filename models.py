from sqlalchemy import (
    Column, String, Text, Integer, Float, ForeignKey,
    BigInteger, DateTime, func, Boolean, Date
)
from db import Base
from sqlalchemy.orm import relationship
import enum

class User(Base):
    __tablename__ = "users"

    id         = Column(BigInteger, primary_key=True, index=True)
    name       = Column(String(100), nullable=False)
    email      = Column(String(255), unique=True, nullable=False)
    password   = Column(Text, nullable=False)
    is_admin   = Column(Boolean, default=False, nullable=False)
    is_blocked = Column(Boolean, default=False, nullable=False)
    failed_login_count   = Column(Integer, default=0, nullable=False)
    onboarding_completed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    body_profile = relationship("body_profile", back_populates="user", uselist=False)
    tokens       = relationship("token", back_populates="user")
    otp_entries  = relationship("PasswordResetOTP", back_populates="user")


class token(Base):
    __tablename__ = "refresh_tokens"

    id                 = Column(BigInteger, primary_key=True, index=True)
    user_id            = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    refresh_token_hash = Column(Text, nullable=False)
    is_remember_me     = Column(Boolean, default=False, nullable=False)
    expires_at         = Column(DateTime(timezone=True), nullable=False)
    revoked_at         = Column(DateTime(timezone=True), nullable=True)
    created_at         = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="tokens")


class PasswordResetOTP(Base):
    __tablename__ = "password_reset_otps"

    id            = Column(BigInteger, primary_key=True, index=True)
    user_id       = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    otp_hash      = Column(Text, nullable=False)
    expires_at    = Column(DateTime(timezone=True), nullable=False)
    consumed_at   = Column(DateTime(timezone=True), nullable=True)
    attempt_count = Column(Integer, default=0, nullable=False)
    created_at    = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="otp_entries")


class body_profile(Base):
    __tablename__ = "body_profiles"

    id             = Column(BigInteger, primary_key=True, index=True)
    user_id        = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    DOB            = Column(Date, nullable=False)
    gender         = Column(String(10), nullable=False)
    height         = Column(Float, nullable=False)
    weight         = Column(Float, nullable=False)
    current_weight_kg=Column(Float, nullable=False)
    activity_level = Column(String(20), nullable=False)
    goal_type      = Column(String(20), nullable=False)
    target_weight  = Column(Float, nullable=True)
    eating_pattern = Column(String(20), nullable=False, default="vegetarian")
    body_type      = Column(String(20), nullable=False)
    bmi_value      = Column(Float, nullable=False)
    bmr            = Column(Float, nullable=False)
    tdee           = Column(Float, nullable=False)
    calories_adjustment = Column(Float, nullable=False)
    daily_calories_target=Column(Float, nullable=False)
    recalculated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
   

    user = relationship("User", back_populates="body_profile")