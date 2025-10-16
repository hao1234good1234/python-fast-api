# 创建借阅服务（Borrow Service）
from core.models import Book, User
from core.interfaces import UserRepository, BookRepository
from core.dtos import UserCreateDto
from core.security import verify_password

# - `LibraryService` 负责 **资源管理**：图书和用户的 **增删改查（CRUD）,以及用户的 **借阅**

class LibraryService:

    # 图书相关方法
    def __init__(self, user_repo: UserRepository, book_repo: BookRepository):
        self.book_repo = book_repo
        self.user_repo = user_repo
    def add_book(self, book: Book) -> None:
        return self.book_repo.save(book)
    def get_book_by_isbn(self, isbn: str) -> Book:
        return self.book_repo.get_by_isbn(isbn)
    def get_all_books(self) -> list[Book]:
        return self.book_repo.get_all()
    def update_book(self, book: Book) -> None:
        return self.book_repo.save(book)
    def delete_book(self, isbn: str) -> bool:
        return self.book_repo.delete(isbn)
    
    # 用户相关方法
    def add_user(self, user_create: UserCreateDto) -> User: # 注意：传入的是带 hashed_password 的 DTO
        # 检查用户名是否已经存在
        existing_user = self.user_repo.get_by_username(user_create.username)
        if existing_user:
            raise ValueError("用户名已存在")
        # 推荐：api调用service的add_user时，已传入已经加密过的密码
        return self.user_repo.add(user_create)
    def get_user_by_id(self, user_id: str) -> User:
        return self.user_repo.get_by_id(user_id)
    def get_all_users(self) -> list[User]:
        return self.user_repo.get_all()
    
    # **重要**：你的 `User` 领域模型 **必须包含 `hashed_password`**，否则无法验证！
    def authenticate_user(self, username: str, password: str) -> User:
        user = self.user_repo.get_by_username(username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    

    # 借阅相关方法
    def borrow_book(self, user: User, isbn: str) -> Book:
        # 1、检查用户是否可用（比如没有封号）
        if not user.is_active:
            raise ValueError("用户账号已被禁用")

        # 2. 检查图书是否存在
        book = self.book_repo.get_by_isbn(isbn)
        if not book:
            raise ValueError("图书不存在")

        # 3. 调用 Book 自己的 borrow 方法！（业务规则在模型内部）
        book.borrow(user.user_id) # ← 这里会自动检查是否已被借

        # 4. 保存更新后的图书状态到数据库
        self.book_repo.save(book)

        # 5. 返回借完后的图书信息（给 API 用）
        return book

    
    def return_book(self, isbn: str) -> None:
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
        self.book_repo.save(book)

    def get_borrows_by_user_id(self, user_id: str) -> list[Book]:
        # 1. 检查用户是否存在
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("用户不存在")
        return self.book_repo.get_borrows_by_user(user_id)
    
    def get_available_books(self) -> list[Book]:
        return self.book_repo.get_all_available()
      