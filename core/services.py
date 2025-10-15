# 创建借阅服务（Borrow Service）
from sqlalchemy.orm import Session
from core.models import Book, User
from infrastructure.interfaces import UserRepository, BookRepository
from infrastructure.book_repository import SqlAlchemyBookRepository
from infrastructure.user_repository import SqlAlchemyUserRepository
from core.dtos import UserCreateDto
from core.security import get_password_hash
# 1. **单一职责原则（SRP）**

# - `LibraryService` 负责 **资源管理**：图书和用户的 **增删改查（CRUD）**
# - `BorrowService` 负责 **业务流程**：借书、还书、查询借阅记录（涉及状态变更和业务规则）

# > 把“管理图书”和“处理借阅”混在一起，会让 `LibraryService` 越来越臃肿，职责不清。
# 2. **业务边界清晰**

# - 图书馆系统中，“图书/用户管理” 和 “借阅流程” 是两个不同的业务域。
# - 未来可能扩展：
#   - 借阅规则（比如每人最多借5本）
#   - 逾期罚款
#   - 预约功能
#   - 借阅历史审计

# 这些都属于 **借阅领域**，不应污染基础资源管理。

class LibraryService:

    # 图书相关方法
    def __init__(self, user_repo: UserRepository, book_repo: BookRepository):
        self.book_repo = book_repo
        self.user_repo = user_repo
    def add_book(self, book: Book) -> Book:
        return self.book_repo.create(book)
    def get_book_by_isbn(self, isbn: str) -> Book:
        return self.book_repo.get_by_isbn(isbn)
    def get_all_books(self) -> list[Book]:
        return self.book_repo.get_all()
    def update_book(self, book: Book) -> Book:
        return self.book_repo.update(book)
    def delete_book(self, isbn: str) -> None:
        return self.book_repo.delete(isbn)
    
    # 用户相关方法
    def add_user(self, user_create: UserCreateDto) -> User: # 注意：传入的是带 password 的 DTO
        existing = self.user_repo.get_by_id(user_create.user_id)
        if existing:
            raise ValueError("用户已存在")
        # 检查用户名是否已经存在
        existing_user = self.user_repo.get_by_username(user_create.username)
        if existing_user:
            raise ValueError("用户名已存在")
        hashed_pw = get_password_hash(user_create.password)
        user = User(
            user_id=user_create.user_id,
            name=user_create.name,
            username=user_create.username,
            is_active=True
        )
        return self.user_repo.create(user, hashed_pw)
    def get_user_by_id(self, user_id: str) -> User:
        return self.user_repo.get_by_id(user_id)
    def get_all_users(self) -> list[User]:
        return self.user_repo.get_all()

        
class BorrowService:
    def __init__(self, user_repo: UserRepository, book_repo: BookRepository):
        self.book_repo = book_repo
        self.user_repo = user_repo

    def borrow_book(self, user_id: str, isbn: str) -> Book:
        # 1、检查用户是否存在
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("用户不存在")

        # 2. 检查图书是否存在
        book = self.book_repo.get_by_isbn(isbn)
        if not book:
            raise ValueError("图书不存在")

        # 3. 检查图书是否已经被借出
        if book.is_borrowed:
            raise ValueError("图书已经被借出")
        # 4. 更新图书的借阅状态
        book.is_borrowed = True
        book.borrowed_by = user_id
        updated_book = self.book_repo.update(book)
        return updated_book
    
    def return_book(self, isbn: str) -> Book:
        # 1. 检查图书是否存在
        book = self.book_repo.get_by_isbn(isbn)
        if not book:
            raise ValueError("图书不存在")
        # 2. 检查图书是否已经被借出
        if not book.is_borrowed:
            raise ValueError("图书未被借出")
        # 3. 还书：重置状态
        book.is_borrowed = False
        book.borrowed_by = None
        updated_book = self.book_repo.update(book)

        return updated_book
    def get_borrows_by_user_id(self, user_id: str) -> list[Book]:
        # 1. 检查用户是否存在
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("用户不存在")
        return self.book_repo.get_borrows_by_user(user_id)
    
    def get_available_books(self) -> list[Book]:
        return self.book_repo.get_all_available()
      