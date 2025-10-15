# 🔧 第一步：定义核心模型（`core/models.py`） 
# dataclass类型
from dataclasses import dataclass


@dataclass
class Book:
    isbn: str  # ISBN是唯一的，这是图书的标识
    title: str  # 书名
    author: str  # 作者
    is_borrowed: bool = False  # 是否借出
    borrowed_by: str | None = None  # 借出用户ID
# ✅ 这个模型包含**业务规则**（比如 `borrow()` 方法），和数据库无关！

@dataclass
class User:
    user_id: str  # 用户ID
    name: str  # 姓名
    username: str  # 用户名
    is_active: bool = True # 是否可用
    # ✅ 不要包含 hashed_password —— domain 层和 API 层都不该接触密码哈希！



# ✅ 用 `dataclass` 简化类，专注业务语义
