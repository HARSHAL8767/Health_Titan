from fastapi import FastAPI,HTTPException,Depends,Header
from pydantic import BaseModel,Field
from typing import List,Dict
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime,timedelta,timezone
import models,schemas
from sqlalchemy.orm import session
from db import engine,sessionLocal
models.Base.metadata.create_all(bind = engine)
from auth import create_token,verify_token,hash_password,verify_password
from schemas import usercreate,userresponse,loginRequast,loginResponse
from crud import createuser,get_user_email,schemas,create_body_profile
from db import get_db
from calculation import ( calculate_age,calculate_bmi,calculate_bmr,calculate_tedd,calcutaed_calories_adjustment,get_body_type)
import crud 





app=FastAPI()
#reister user

@app.post("/register",response_model=userresponse)
def register(user:usercreate,db:session=Depends(get_db)):
    return createuser(db,user)

# login user

@app.post("/login",response_model=loginResponse)
def login(data:loginRequast,db:session=Depends(get_db)):
    # email varify
    user=get_user_email(db,data.email)


    if not user:
        raise HTTPException(status_code= 401,detail="invalid password")
    #password verify
    if not verify_password(data.password,user.password):
        raise HTTPException(status_code=401,detail="invalid email or password ")
    
    access_token1=create_token(data= 
                              {
                                  "user_id":user.id,
                                  "is_admin":user.is_admin
                              })
    return loginResponse(
        massage="login successfull",
        access_token=access_token1,
        token_type="bearer"
    )
    
# @app.get("/profile")
# def check_token(token:str=Header(None)):
#     payload=verify_token(token)
#     return {
#         "valid":True,
#         "paayload":payload
#     }

#  user profile information

@app.post("/body_profile",response_model=schemas.body_profileResponce)
def create_profile(
    data:schemas.Body_Profile_create,
    db:session=Depends(get_db),
    user_data:dict=Depends(verify_token)
):
    user_id = user_data.get("user_id")
    return crud.create_body_profile(db,user_id,data)

# user dashbord 

@app.get("/dashbord",response_model=schemas.body_profileResponce)
def dashbord(
    db:session=Depends(get_db),
    user_data:dict=Depends(verify_token)
):
    user_id=user_data.get("user_id")
    profile=db.query(models.body_profile).filter(models.body_profile.user_id==user_id).first()
    return profile