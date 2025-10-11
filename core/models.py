# 🔧 第一步：定义核心模型（`core/models.py`）
from dataclasses import dataclass


@dataclass
class Book:
    isbn: str  # ISBN是唯一的，这是图书的标识
    title: str  # 书名
    author: str  # 作者
    is_borrowed: bool = False  # 是否借出
    borrowed_by: str | None = None  # 借出用户ID


@dataclass
class User:
    user_id: str  # 用户ID
    name: str  # 姓名


# ✅ 用 `dataclass` 简化类，专注业务语义
