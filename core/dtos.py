from dataclasses import dataclass
from datetime import datetime, timezone

@dataclass
class UserCreateDto:
    user_id: str
    name: str
    email: str
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

# 创建该dto就是为了返回书名，该类除了title外，其他字段与BorrowRecord相同
@dataclass
class BorrowRecordDto:
    id: int
    book_isbn: str
    book_title: str
    borrower_id: str
    borrowed_at: datetime
    due_date: datetime
    returned_at: datetime | None
    is_returned: bool
    is_overdue: bool
    
    @property # 是否已归还，可计算
    def is_book_returned(self) -> bool:
        return self.returned_at is not None
    
    # `is_book_overdue` 是 **只读属性（property）**，自动计算
    # 业务规则 **内聚在模型中**，外部无需知道“超期 = now > due_date and not returned”
    @property # 是否逾期，可计算
    def is_book_overdue(self) -> bool:
        """自动计算是否超期：已过 due_date 且未归还"""
        if self.is_book_returned: # 已归还，如果归还时间大于应还时间，就是逾期
            return self.returned_at > self.due_date
        return datetime.now(timezone.utc) > self.due_date
    
    def mark_returned(self):
        """归还操作封装到模型内部"""
        if self.is_returned:
            raise ValueError("图书已归还")
        self.returned_at = datetime.now(timezone.utc)

@dataclass
class MyBorrowDto:
    items: list[BorrowRecordDto]
    total: int
    page: int
    size: int
    pages: int


    
