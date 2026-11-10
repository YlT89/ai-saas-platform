from pydantic import BaseModel, ConfigDict
from typing import Optional



class AddressCreate(BaseModel):
    province: str
    city: str
    detail: str


class AddressUpdate(BaseModel):
    province: Optional[str] = None
    city: Optional[str] = None
    detail: Optional[str] = None


class AddressPublic(BaseModel):
    id: int
    province: str
    city: str
    detail: str



    model_config = ConfigDict(from_attributes=True)