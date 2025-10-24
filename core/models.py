# 🔧 第一步：定义核心模型（`core/models.py`） 
# dataclass类型
from dataclasses import dataclass
from datetime import datetime, timezone
# ✅ 用 `dataclass` 简化类，专注业务语义
# 在 @dataclass 中，所有没有默认值的字段必须写在有默认值的字段前面。

# 领域模型

@dataclass
class Book:
    isbn: str  # ISBN 是图书的唯一标识（比如 978-7-111-12345-6）
    title: str  # 书名
    author: str  # 作者
    is_borrowed: bool = False  # 是否已被借出？默认 False（可借）   
    borrowed_by: str | None = None  # 借出用户ID 存用户ID（user_id）
    # ✅ 这个模型包含**业务规则**（比如 `borrow()` 方法），和数据库无关！
    # 👇 这是“业务行为”：借书！
    def borrow(self, user_id: str) -> None:
        # 检查，如果已经借出了，就不能再借
        if self.is_borrowed:
            raise ValueError("图书已经被借出")
        # 执行借书：标记为已借出，并记录借书人
        self.is_borrowed = True
        self.borrowed_by = user_id

    # 还书行为 （后面会用到）
    def return_cook(self) -> None:
        if not self.is_borrowed:
            raise ValueError("图书未被借出")
        self.is_borrowed = False
        self.borrowed_by = None
        
# ✅ 重点：**领域模型 = 业务规则 + 数据**，不是数据库表！

@dataclass
class User:
    user_id: str   # 用户唯一ID（比如 UUID）
    username: str   # 登录用的用户名
    name: str  # 真实姓名
    email: str
    hashed_password: str   # 密码（已经加密过的，不能是明文！）
    is_active: bool = True # 用户是否可用？默认是（防止被封号）

    # ✅ 不要包含 hashed_password —— domain 层和 API 层都不该接触密码哈希！

@dataclass
class BorrowRecord:
    id: int | None    # 新借书时为 None
    book_isbn: str 
    borrower_id: str # 借书人 ID（比如用户 ID）
    borrowed_at: datetime # 借书时间
    due_date: datetime   # 应还日期（比如借7天）
    returned_at: datetime | None = None # 实际归还时间
    is_returned: bool = False   # 是否还书（持久化）
    is_overdue: bool = False # 是否逾期（持久化）

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




