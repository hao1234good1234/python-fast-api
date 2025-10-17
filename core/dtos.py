from dataclasses import dataclass
from datetime import datetime

@dataclass
class UserCreateDto:
    user_id: str
    name: str
    username: str
    hashed_password: str # **在 DTO 中直接存 `hashed_password`**
    is_active: bool = True

@dataclass 
class ReturnBookDto:
    borrow_id: int
    book_isbn: str
    returned_at: datetime
    is_overdue: bool

@dataclass
class BorrowBookDto:
    borrow_id: int
    book_isbn: str
    borrower_id: str
    borrowed_at: datetime
    due_date: datetime


    
