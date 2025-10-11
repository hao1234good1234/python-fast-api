#  第二步：定义抽象接口（`core/interfaces.py`）
from typing import Protocol
from .models import Book, User


class BookRepository(Protocol):  # 定义图书接口
    def get_by_isbn(self, isbn: str) -> Book | None: ...  # 根据 isbn 获取图书
    def save(self, book: Book) -> None: ...  # 保存图书
    def list_all(self) -> list[Book]: ...  # 获取所有图书


class UserRepository(Protocol):  # 定义用户接口
    def get_by_id(self, user_id: str) -> User | None: ...  # 根据 id 获取用户
    def save(self, user: User) -> None: ...  # 保存用户


# ✅ 这就是你学的 `Protocol` —— 定义“角色”，不绑定实现
