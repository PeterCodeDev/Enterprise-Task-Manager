from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)


class UserResponse(BaseModel):
    id: int
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None


class CategoryCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    color: str = Field(default="#4361ee", max_length=7)


class CategoryResponse(BaseModel):
    id: int
    nombre: str
    color: str

    model_config = {"from_attributes": True}


class TaskCreate(BaseModel):
    titulo: str = Field(..., min_length=1, max_length=255)
    descripcion: Optional[str] = Field(None, max_length=1000)
    category_ids: List[int] = Field(default_factory=list)


class TaskUpdate(BaseModel):
    titulo: str = Field(..., min_length=1, max_length=255)
    descripcion: Optional[str] = Field(None, max_length=1000)
    category_ids: List[int] = Field(default_factory=list)


class TaskResponse(BaseModel):
    id: int
    titulo: str
    descripcion: Optional[str]
    completada: bool
    user_id: int
    categories: List[CategoryResponse] = []

    model_config = {"from_attributes": True}
