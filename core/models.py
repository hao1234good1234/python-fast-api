# 🔧 第一步：定义核心模型（`core/models.py`）
from dataclasses import dataclass


@dataclass
class Book:
    isbn: str  # ISBN是唯一的，这是图书的标识
    title: str  # 书名
    author: str  # 作者
    is_borrowed: bool = False  # 是否借出
    borrowed_by: str | None = None  # 借出用户ID

    def borrow(self, user_id: str) -> bool:
        """借书逻辑，只有未借出的图书才能借出"""
        if not self.is_borrowed:
            self.is_borrowed = True
            self.borrowed_by = user_id
            return True
        return False
    def return_book(self) -> bool:
        """还书逻辑，只有已借出的图书才能还书"""
        if self.is_borrowed:
            self.is_borrowed = False
            self.borrowed_by = None
            return True
        return False
# ✅ 这个模型包含**业务规则**（比如 `borrow()` 方法），和数据库无关！

@dataclass
class User:
    user_id: str  # 用户ID
    name: str  # 姓名
    # password_hash: str  # ← 敏感！不能返回给前端

# ✅ 用 `dataclass` 简化类，专注业务语义
