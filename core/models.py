# 🔧 第一步：定义核心模型（`core/models.py`） 
# dataclass类型
from dataclasses import dataclass

# 在 @dataclass 中，所有没有默认值的字段必须写在有默认值的字段前面。

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
    hashed_password: str   # 密码（已经加密过的，不能是明文！）
    is_active: bool = True # 用户是否可用？默认是（防止被封号）

    # ✅ 不要包含 hashed_password —— domain 层和 API 层都不该接触密码哈希！




# ✅ 用 `dataclass` 简化类，专注业务语义
