from pydantic import BaseModel, EmailStr, ConfigDict


class ClientRegisterResponse(BaseModel):
    client_id: int
    access_tokens: str
    tokens_type: str
    message: str

class ClientLogin(BaseModel):
    email: EmailStr
    password: str


class DriverRegisterResponse(BaseModel):
    driver_id: int
    access_tokens: str
    tokens_type: str
    message: str

class DriverLogin(BaseModel):
    email: EmailStr
    password: str


class HelperRegisterResponse(BaseModel):
    helper_id: int
    access_tokens: str
    tokens_type: str
    message: str

class HelperLogin(BaseModel):
    email: EmailStr
    password: str

class Tokens(BaseModel):
    access_tokens: str
    refresh_tokens: str
    tokens_type: str

    model_config = ConfigDict(from_attributes=True)


class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    code: str
    new_password: str

class TwoFAValidateRequest(BaseModel):
    email: EmailStr
    code: str