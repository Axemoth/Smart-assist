from typing import List
from pydantic import BaseModel, EmailStr, ConfigDict, NameEmail

class User(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str

class UserBase(BaseModel):
    email: EmailStr
    password: str

class RegisterRequest(UserBase):
    name: str
    role: str

class RegisterResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    message: str
    email: EmailStr

class LoginRequest(UserBase):
    ...

class RefreshToken(BaseModel):
    refresh_token: str

class VerifyMailModel(BaseModel):
    message: str
