from pydantic import BaseModel, EmailStr, model_validator, Field
from datetime import datetime, date
from typing import Optional
from enum import Enum

# ─── Enums ───
class GenderEnum(str, Enum):
    male   = "male"
    female = "female"
    other  = "other"

class ActivityEnum(str, Enum):
    sedentary   = "sedentary"
    light       = "light"
    moderate    = "moderate"
    active      = "active"
    very_active = "very_active"

class GoalEnum(str, Enum):
    lose     = "lose"
    gain     = "gain"
    maintain = "maintain"

class EatingPatternEnum(str, Enum):
    vegetarian     = "vegetarian"
    non_vegetarian = "non_vegetarian"
    vegan          = "vegan"

# ─── User ───
class usercreate(BaseModel):
    name:             str
    email:            EmailStr
    password:         str
    confirm_password: str

    @model_validator(mode="after")
    def check_password_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Password and confirm password do not match")
        if len(self.password) < 8:
            raise ValueError("Password must be at least 8 characters")
        return self

class userresponse(BaseModel):
    id:         int
    name:       str
    email:      str
    is_admin:   bool
    created_at: datetime
    class Config:
        from_attributes = True

# ─── Login ───
class loginrequest(BaseModel):
    email:       EmailStr
    password:    str
    remember_me: bool = False          # ← Remember Me field

class loginresponse(BaseModel):
    access_token:  str
    token_type:    str = "bearer"
    message:       str = "Login successful"

# ─── Forgot Password ───
class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ForgotPasswordResponse(BaseModel):
    message: str

# ─── Verify OTP ───
class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp:   str

class VerifyOTPResponse(BaseModel):
    message:      str
    reset_token:  str        # short-lived token to authorize the actual reset

# ─── Reset Password ───
class ResetPasswordRequest(BaseModel):
    reset_token:      str
    new_password:     str
    confirm_password: str

    @model_validator(mode="after")
    def passwords_match(self):
        if self.new_password != self.confirm_password:
            raise ValueError("Passwords do not match")
        if len(self.new_password) < 8:
            raise ValueError("Password must be at least 8 characters")
        return self

class ResetPasswordResponse(BaseModel):
    message: str

# ─── Body Profile ───
class Body_Profile_create(BaseModel):
    DOB:            date
    gender:         GenderEnum
    height:         float = Field(..., gt=0)
    weight:         float = Field(..., gt=0)
    activity_level: ActivityEnum
    goal_type:      GoalEnum
    target_weight:  Optional[float] = None
    eating_pattern: EatingPatternEnum = EatingPatternEnum.vegetarian

class Body_Profile_response(BaseModel):
    id:                  int
    user_id:             int
    DOB:                 date
    gender:              str
    height:              float
    weight:              float
    activity_level:      str
    goal_type:           str
    target_weight:       Optional[float]
    eating_pattern:      str
    body_type:           str
    bmi_value:           float
    bmr:                 float
    tdee:                float
    calories_adjustment: float
    recalculated_at:     datetime
    class Config:
        from_attributes = True