#  第二步：定义抽象接口（`core/interfaces.py`）
from abc import ABC, abstractmethod
from .models import Book, User, BorrowRecord
from .dtos import UserCreateDto

class BookRepository(ABC):
    @abstractmethod
    def get_by_isbn(self, isbn: str) -> Book | None: 
        pass
    @abstractmethod
    def get_all(self) -> list[Book]: 
        pass
    @abstractmethod
    def save(self, book: Book) -> None:
        """保存图书状态（无论是新建还是修改）"""
        pass
    @abstractmethod
    def delete(self, isbn: str) -> bool:
        pass
    @abstractmethod
    def get_borrows_by_user(self, user_id: str) -> list[Book]:
        pass
    @abstractmethod
    def get_all_available(self) -> list[Book]:
        pass
class UserRepository(ABC):
    @abstractmethod
    def add(self, user: UserCreateDto) -> User:
        pass
    @abstractmethod
    def get_by_id(self, user_id: str) -> User | None:
        pass
    @abstractmethod
    def get_all(self) -> list[User]:
        pass
    @abstractmethod
    def get_by_username(self, username: str) -> User | None:
        pass

class BorrowRepository(ABC):
    @abstractmethod
    def create(self, borrow_record: BorrowRecord) -> BorrowRecord:
        pass

    @abstractmethod
    def get_by_id(self, borrow_id: int) -> BorrowRecord |None:
        pass
    @abstractmethod
    def save(self, borrow_record: BorrowRecord) -> None:
        pass

    # 返回：元组(记录列表, 总数量)
    @abstractmethod
    def get_borrows_by_user(self, user_id: str, page: int = 1, size: int = 10) -> tuple[list[BorrowRecord], int]:
        pass

