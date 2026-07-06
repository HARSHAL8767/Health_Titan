from sqlalchemy import Column, String,Text,Integer,Float,ForeignKey,BigInteger,DateTime,func,Boolean,Date,CheckConstraint
from db import Base
from sqlalchemy.orm import relationship
from datetime import datetime,timedelta,timezone

class User(Base):
    __tablename__="users"

    id=Column(BigInteger,primary_key=True,index=True)
    username=Column(String(100),nullable=False)
    email=Column(String(100),unique=True,nullable=False)
    password=Column(Text,nullable=False)
    is_admin=Column(Boolean,default=False,nullable=False)
    created_at=Column(DateTime(timezone=True),
                      server_default=func.now(),nullable= False)
    
class body_profile(Base):
    __tablename__="body_profile"

    id=Column(BigInteger,primary_key=True,index=True)
    user_id=Column(Integer,ForeignKey("users.id"),unique=True)
    # ui fields
    DOB= Column(Date)
    gender=Column(String)
    height=Column(Float)
    weight=Column(Float)
    activity_level=Column(String)
    goal_type=Column(String)
    target_weight=Column(Float)

    # bacend calculation 
    body_type=Column(String)
    bmi_value=Column(Float)
    bmr=Column(Float)
    tdee=Column(Float)
    calories_adjustment=Column(Float)
    eating_pattern=Column(String,nullable=False,default="vegitarian")
    recalculated_at=Column(DateTime,default=lambda:datetime.now(timezone.utc))

    __table_args__=(
        CheckConstraint(
            "eating_patter in ('vegetarien','non_vegetarian','vegan')",
            name="check_eating_patter"
        ),
    )








    