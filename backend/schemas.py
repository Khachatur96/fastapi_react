from datetime import datetime

from pydantic import BaseModel


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    hashed_password: str

    class Config:
        orm_mode = True


class User(UserBase):
    id: int

    class Config:
        orm_mode = True


class LeadBase(BaseModel):
    first_name: str
    last_name: str
    email: str
    company: str
    note: str


class LeadCreate(LeadBase):
    pass


class Lead(LeadBase):
    id: int
    owner_id: int
    date_created: datetime
    date_last_updated: datetime

    class Config:
        orm_mode = True
