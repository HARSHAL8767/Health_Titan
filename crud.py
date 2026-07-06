from models import User
from sqlalchemy.orm import session
from auth import hash_password,verify_password
from datetime import datetime,timezone


def createuser(db,user):
    print("createuser called")
    print("password from request:",user.password)
    print(len(user.password))
    print(type(user.password))
    hashed_password=hash_password(user.password)
    
    db_user=User(
        username=user.username,
        email=user.email,
        password=hashed_password,
        is_admin=False
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    

    return db_user

def get_user_email(db:session,email:str):
    return  db.query(User).filter(User.email==email).first()



# body profile
from calculation import ( calculate_age,calculate_bmi,calculate_bmr,calculate_tedd,calcutaed_calories_adjustment,get_body_type)
from datetime import datetime,timezone
import models,schemas
from sqlalchemy.orm import session

def create_body_profile(db:session,user_id:int,data:schemas.Body_Profile_create):
    age=calculate_age(data.DOB)
    bmi=calculate_bmi(data.weight,data.height)
    body_type=get_body_type(bmi)
    bmr=calculate_bmr(data.weight,data.height,age,data.gender)
    tdee=calculate_tedd(bmr,data.activity_level)
    calorie_adj=calcutaed_calories_adjustment(tdee,data.goal_type)

    profile=models.body_profile(
        user_id=user_id,
        DOB=data.DOB,
        gender=data.gender,
        height=data.height,
        weight=data.weight,
        activity_level=data.activity_level,
        goal_type=data.goal_type,
        target_weight=data.target_weight,
        body_type=body_type,
        bmi_value=bmi,
        bmr=bmr,
        tdee=tdee,
        calories_adjustment=calorie_adj,
        eating_pattern=data.eating_pattern.value,
        recalculated_at=datetime.now(timezone.utc)

    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile

{
  "DOB": "2026-07-05",
  "gender": "male",
  "height": 170,
  "weight": 60,
  "activity_level": "moderate",
  "goal_type": "lose",
  "target_weight": 65
}

# eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjo5LCJleHAiOjE3ODMyNDc4MzN9._KUsAF3QUHu9bPb1vdXrF43Z8gtwNusi2jCUkVXSqgI