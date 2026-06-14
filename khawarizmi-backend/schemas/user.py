from typing import Dict, Any, Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    email:    EmailStr
    password: str = Field(min_length=8, max_length=100)
    prenom:   str = Field(min_length=2, max_length=50)
    wilaya:   Optional[str] = None
    filiere:  str = Field(default="sciences")

    @field_validator("password")
    @classmethod
    def password_strength(cls, v):
        if v.isdigit():
            raise ValueError("Le mot de passe ne peut pas être que des chiffres")
        return v


class LoginRequest(BaseModel):
    email:    EmailStr
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"
    user:         Dict[str, Any]


class WaitlistRequest(BaseModel):
    name:   str       = Field(min_length=2, max_length=50)
    email:  EmailStr
    wilaya: Optional[str] = None
    lang:   str       = "fr"
    source: Optional[str] = None
