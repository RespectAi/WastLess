# app/schemas.py

from pydantic import BaseModel, EmailStr
from datetime import datetime, date
from typing import Optional, List, Literal


# Shared properties
class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None

# Properties for user creation
class UserCreate(UserBase):
    password_hash: str

# Properties returned to client
class UserRead(UserBase):
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True  # tells Pydantic to read data from ORM objects

# Shared fridge fields
class FridgeBase(BaseModel):
    name: str
    location_desc: Optional[str] = None

# For creation
class FridgeCreate(FridgeBase):
    pass  # same as Base

# For reading (include ID and timestamps)
class FridgeRead(FridgeBase):
    fridge_id: int
    created_at: datetime

    class Config:
        orm_mode = True

# For sharing a fridge
class FridgeUserBase(BaseModel):
    user_id: int
    role: Literal['owner', 'editor', 'viewer']  # restrict to allowed values

class FridgeUserCreate(FridgeUserBase):
    pass

# For reading shared‐with entries
class FridgeUserRead(FridgeUserBase):
    fridge_id: int

    class Config:
        orm_mode = True
       
# Shared fields for FridgeItem
class FridgeItemBase(BaseModel):
    qr_code: str
    factory_expires_at: date
    opened_at: Optional[date] = None
    open_life_days: int

# For creation
class FridgeItemCreate(FridgeItemBase):
    added_by: int  # user_id of the person adding

# For updates (you can change opened_at or open_life_days)
class FridgeItemUpdate(BaseModel):
    opened_at: Optional[date] = None
    open_life_days: Optional[int] = None

# For reading
class FridgeItemRead(FridgeItemBase):
    item_id: int
    fridge_id: int
    added_by: int
    added_at: datetime
    spoil_date: date

    class Config:
        orm_mode = True      


# Shared notification fields
class NotificationBase(BaseModel):
    item_id: int
    user_id: int
    type: Literal['about_to_spoil', 'spoiled']
    sent: bool = False

# For creation (we’ll auto-set notified_at in CRUD)
class NotificationCreate(NotificationBase):
    pass

# For reading
class NotificationRead(NotificationBase):
    note_id: int
    notified_at: datetime

    class Config:
        orm_mode = True
