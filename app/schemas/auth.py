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

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    code: str
    new_password: str

class TwoFAValidateRequest(BaseModel):
    email: EmailStr
    code: str