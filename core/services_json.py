# ⚙️ 第三步：实现核心业务逻辑（`core/services.py`）
from .models import Book
from .interfaces import UserRepository, BookRepository
import logging  # 👈 只用于 getLogger，不配置！

# 创建一个 logger，名字通常是当前模块名
logger = logging.getLogger(__name__)

# json
class LibraryService:
    def __init__(self, book_repo: BookRepository, user_repo: UserRepository):
        self._book_repo = book_repo
        self._user_repo = user_repo

    def add_book(self, isbn: str, title: str, author: str) -> Book:  # 添加图书
        book = Book(isbn=isbn, title=title, author=author)
        self._book_repo.save(book)
        logger.info(f"图书 {title} 添加成功")
        return book

    def borrow_book(self, isbn: str, user_id: str) -> bool:  # 借阅图书
        book = self._book_repo.get_by_isbn(isbn)
        user = self._user_repo.get_by_id(user_id)
        if not book or not user:
            return False
        if book.is_borrowed:
            return False
        book.is_borrowed = True
        book.borrowed_by = user_id
        self._book_repo.save(book)
        logger.info(f"用户 {user.name} 借阅了图书 {book.title}")
        return True

    def return_book(self, isbn: str) -> bool:  # 还书
        book = self._book_repo.get_by_isbn(isbn)
        if not book or not book.is_borrowed:
            return False
        book.is_borrowed = False
        book.borrowed_by = None
        self._book_repo.save(book)
        logger.info(f"图书 {book.title} 还书成功")
        return True

    def is_available(self, isbn: str) -> bool:  # 图书是否可借阅
        book = self._book_repo.get_by_isbn(isbn)
        return book is not None and not book.is_borrowed

    def get_user_books(self, user_id: str) -> list[Book]:  # 获取用户借阅的图书
        all_books = self._book_repo.list_all()
        return [b for b in all_books if b.borrowed_by == user_id]

    def get_book_by_isbn(self, isbn: str) -> Book | None:  # 根据 isbn 获取图书
        return self._book_repo.get_by_isbn(isbn)
    
    def get_all_books(self) -> list[Book]:  # 获取所有图书
        return self._book_repo.list_all()


# ✅ **关键点**：

# - `LibraryService` **只依赖 Protocol**，不关心存储在哪
# - 业务逻辑清晰，无技术细节（如数据库、文件）
