from sqlmodel import SQLModel
from pydantic import EmailStr, field_validator, Field
from typing import Optional, List
from schemas.address_schemas import AddressPublic
from datetime import datetime
import re


class UserBase(SQLModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str

    @field_validator('password')
    def check_password_strength(cls, v):
        # 1. 长度校验
        if len(v) < 8:
            raise ValueError("密码长度不能少于8位")

        # 2. 包含大写字母
        if not re.search(r'[A-Z]', v):
            raise ValueError("密码必须包含大写字母")

        # 3. 包含小写字母
        if not re.search(r'[a-z]', v):
            raise ValueError("密码必须包含小写字母")

        # 4. 包含数字
        if not re.search(r'[0-9]', v):
            raise ValueError("密码必须包含数字")

        return v


class UserUpdate(SQLModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None


class UserPublic(UserBase):
    id: int
    role: str
    disabled: bool
    create_time: datetime
    addresses: List[AddressPublic] = Field(default_factory=list)