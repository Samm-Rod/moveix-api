from pydantic import BaseModel, EmailStr

class ClientLogin(BaseModel):
    email: EmailStr
    password: str

class DriverLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str 
    token_type: str 

