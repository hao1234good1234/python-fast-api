from abc import ABC, abstractmethod
from core.models import Book, User

class BookRepository(ABC):
    @abstractmethod
    def create(self, book: Book) -> Book: 
        pass
    @abstractmethod
    def get_by_isbn(self, isbn: str) -> Book | None: 
        pass
    @abstractmethod
    def get_all(self) -> list[Book]: 
        pass
    @abstractmethod
    def update(self, book: Book) -> Book:
        pass
    @abstractmethod
    def delete(self, isbn: str) -> None:
        pass
    @abstractmethod
    def get_borrows_by_user(self, user_id: str) -> list[Book]:
        pass
    @abstractmethod
    def get_all_available(self) -> list[Book]:
        pass
class UserRepository(ABC):
    @abstractmethod
    def create(self, user: User) -> User:
        pass
    @abstractmethod
    def get_by_id(self, user_id: str) -> User | None:
        pass
    @abstractmethod
    def get_all(self) -> list[User]:
        pass
