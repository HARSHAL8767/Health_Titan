from jose import jwt,JWTError
from fastapi import FastAPI ,Depends,HTTPException,Header
from datetime import datetime,timedelta,timezone
from fastapi.security import OAuth2AuthorizationCodeBearer
from passlib.context import CryptContext

SECRET_KEY="my_secret"
ALGORITHM="HS256"
token_access_time=30

def create_token(data:dict):
   to_encode =data.copy()
   expire=datetime.now(timezone.utc)+timedelta(minutes=token_access_time)
   to_encode.update({
      "exp":expire
   })

   token=jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
   return token 

def verify_token(token:str=Header(None)):
   try:
      payload=jwt.decode(token,SECRET_KEY,algorithms=ALGORITHM)
      return payload
   except JWTError:
      raise HTTPException(status_code=401,detail="invalid token")
   

# password hash
#    
pwt_context=CryptContext( 
   schemes=["bcrypt"],
   deprecated="auto"
   )

def hash_password(password:str):
   return pwt_context.hash(password)

def verify_password(plain_password:str,hashed_password:str):
   pwt_context.verify(plain_password,hashed_password)

   return pwt_context.verify(plain_password,hashed_password)
