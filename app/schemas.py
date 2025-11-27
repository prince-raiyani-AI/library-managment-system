from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# --- User Schemas ---
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str
    pin: Optional[str] = None # For staff registration

class UserLogin(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_staff: bool
    created_at: datetime

    class Config:
        orm_mode = True

# --- Book Schemas ---
class BookBase(BaseModel):
    title: str
    author: str
    description: Optional[str] = None
    price: float
    quantity: int
    image_url: Optional[str] = None

class BookCreate(BookBase):
    pass

class BookUpdate(BookBase):
    pass

class BookResponse(BookBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

# --- Transaction Schemas ---
class TransactionBase(BaseModel):
    book_id: int
    transaction_type: str # 'buy' or 'borrow'

class TransactionCreate(TransactionBase):
    pass

class TransactionResponse(TransactionBase):
    id: int
    user_id: int
    amount: float
    due_date: Optional[datetime] = None
    return_date: Optional[datetime] = None
    is_returned: bool
    created_at: datetime

    class Config:
        orm_mode = True
