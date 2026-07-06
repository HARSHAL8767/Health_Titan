from pydantic import BaseModel,EmailStr,model_validator
from datetime import datetime,timedelta,date
from typing import Optional
from enum import Enum
class usercreate(BaseModel):
    username:str
    email:str
    password:str
    confirm_password:str
#auto validate password and confirm password 
    @model_validator(mode="after")
    def check_password_match(self):
         if self.password != self.confirm_password:
              raise ValueError("password and conform password does not match")
         return self

    

class userresponse(BaseModel):
    id:int
    username:str
    email:str
    is_admin:bool
    created_at:datetime

    class Config:
        from_attributes=True

class loginRequast(BaseModel):
    email:EmailStr
    password:str

class loginResponse(BaseModel):
    massage:str
    access_token:str
    token_type:str

class Eatingpatter(str,Enum):
     vegetarien="vegeterian"
     non_vegetarian="non_vegetarian"
     vegan="vegan"

class Body_Profile_create(BaseModel):
    DOB:date
    gender:str
    height:float
    weight:float
    activity_level:str
    goal_type:str
    target_weight:Optional[float]=None
    eating_pattern:Eatingpatter

    #update (dashbord )
class body_profile_update(BaseModel):
        weight:Optional[float]=None
        activity_level:Optional[str]=None
        goal_type:Optional[str]=None
        target_weight:Optional[float]=None
 
class body_profileResponce(BaseModel):
    id:int
    user_id:int
    DOB:date
    gender:str
    height:float
    weight:float
    activity_level:str
    goal_type:str
    target_weight:Optional[float]
    body_type:str
    bmi_value:float
    bmr:float
    tdee:float
    calories_adjustment:float
    eating_pattern:Eatingpatter
    recalculated_at:datetime

    class config:
         from_attributes=True
         
