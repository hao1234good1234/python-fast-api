# 创建借阅服务（Borrow Service）
from core.models import Book, User, BorrowRecord
from core.interfaces import UserRepository, BookRepository, BorrowRepository
from core.dtos import UserCreateDto, ReturnBookDto, BorrowBookDto, MyBorrowDto
from core.security import verify_password
from datetime import datetime, timedelta, timezone
from core.exceptions import (
    BookNotFoundError,
    BookNotAvailableError,
    BorrowRecordNotFoundError,
    PermissionError,
    BookAlreadyReturnError,
    UsernameExistsError,
    BookExistsError,
)
from core.logger import get_logger
logger = get_logger(__name__)

# - `LibraryService` 负责 **资源管理**：图书和用户的 **增删改查（CRUD）,以及用户的 **借阅**
BORROW_DURATION_DAYS = 7  # 借阅期限：7天


class LibraryService:
    # 图书相关方法
    def __init__(self, user_repo: UserRepository, book_repo: BookRepository):
        self.book_repo = book_repo
        self.user_repo = user_repo

    def add_book(self, book: Book) -> None:
        existing = self.book_repo.get_by_isbn(book.isbn)
        if existing:
            raise BookExistsError(book.isbn)
        return self.book_repo.save(book)

    def get_book_by_isbn(self, isbn: str) -> Book:
        return self.book_repo.get_by_isbn(isbn)

    def get_all_books(self) -> list[Book]:
        return self.book_repo.get_all()

    def update_book(self, book: Book) -> None:
        existing = self.book_repo.get_by_isbn(book.isbn)
        if not existing:
            raise BookNotFoundError(book.isbn)
        return self.book_repo.save(book)

    def delete_book(self, isbn: str) -> bool:
        return self.book_repo.delete(isbn)

    # 用户相关方法
    def add_user(
        self, user_create: UserCreateDto
    ) -> User:  # 注意：传入的是带 hashed_password 的 DTO
        # 检查用户名是否已经存在
        username = user_create.username
        existing_user = self.user_repo.get_by_username(username)
        if existing_user:
            raise UsernameExistsError(username)
        # 推荐：api调用service的add_user时，已传入已经加密过的密码
        return self.user_repo.add(user_create)

    def get_user_by_id(self, user_id: str) -> User:
        return self.user_repo.get_by_id(user_id)

    def get_all_users(self) -> list[User]:
        return self.user_repo.get_all()

    def get_user_by_username(self, username: str) -> User:
        return self.user_repo.get_by_username(username)

    # **重要**：你的 `User` 领域模型 **必须包含 `hashed_password`**，否则无法验证！
    def authenticate_user(self, username: str, password: str) -> User:
        user = self.user_repo.get_by_username(username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user


class BorrowService:
    def __init__(self, book_repo: BookRepository, borrow_repo: BorrowRepository):
        self.book_repo = book_repo
        self.borrow_repo = borrow_repo

    # 借书
    def borrow_book(self, isbn: str, borrower_id: str) -> BorrowBookDto:


        # 1、检查图书是否存在
        book = self.book_repo.get_by_isbn(isbn)
        if not book:
            raise BookNotFoundError(isbn)
        # 2. 检查是否已经被借出
        if book.is_borrowed:
            raise BookNotAvailableError(isbn, book.title)

        # 3. 创建借阅记录
        # 存储用 UTC，展示用本地时区
        now = datetime.now(timezone.utc)
        due_date = now + timedelta(days=BORROW_DURATION_DAYS)  # 借阅期限为 7 天
        borrow = BorrowRecord(
            id=None,  # 新记录，ID 由数据库生成
            book_isbn=book.isbn,
            borrower_id=borrower_id,
            borrowed_at=now,
            due_date=due_date,
        )

        # 4. 保存借阅记录
        saved_borrow = self.borrow_repo.create(borrow)

        # 5. 更新图书的状态
        book.is_borrowed = True
        book.borrowed_by = borrower_id
        self.book_repo.save(book)

        # 记录结构化日志
        # 🔑 关键点：
        # - 使用 `extra={}` 传入结构化字段
        # - `event` 字段便于日志系统做分类统计（如告警、仪表盘）
        # - **不要记录敏感信息**（如密码、完整 token）

        # 结构化日志
        # 总结：你只需要记住三件事
        # 1. **写日志用 `logger.info("消息", extra={结构化数据})`**
        # 2. **开发看文字，生产看 JSON**
        # 3. **敏感信息（密码、token）绝对不要打日志！**
        logger.info(
            "用户借了一本书",
            extra={  # 结构化数据（电脑用的），`extra={}` 是 Python 日志的特殊参数，用来传**额外字段**，这些字段会被 `CustomJsonFormatter` 自动放进 JSON 里
                "event": "BOOK_BORROWED",
                "user_id": borrower_id,
                "book_isbn": isbn,
                "book_title": book.title,
                "borrow_date": str(datetime.now(timezone.utc).date()),
            }
        )

       



        # 6. 返回结果
        return BorrowBookDto(
            borrow_id=saved_borrow.id,
            book_isbn=saved_borrow.book_isbn,
            borrower_id=saved_borrow.borrower_id,
            borrowed_at=saved_borrow.borrowed_at,
            due_date=saved_borrow.due_date,
        )

    # 还书
    def return_book(
        self, borrow_id: int, current_user_id: str
    ) -> ReturnBookDto:  # borrow_id是borrows表的主键id
        # 1. 查找借阅记录
        borrow = self.borrow_repo.get_by_id(borrow_id)
        if not borrow:
            raise BorrowRecordNotFoundError(borrow_id)
        # 2. 【关键】权限校验：是否属于当前用户？
        if borrow.borrower_id != current_user_id:
            raise PermissionError(current_user_id, borrow.borrower_id)
        # 3.检查是否归还
        if borrow.is_returned:
            raise BookAlreadyReturnError(borrow_id)
        # 4.检查是否逾期
        now = datetime.now(timezone.utc)
        is_overdue = now > borrow.due_date

        # 5. 更新借阅记录
        borrow.returned_at = now
        borrow.is_returned = True
        borrow.is_overdue = is_overdue

        # 6. 保存借阅记录
        self.borrow_repo.save(borrow)

        # 7.更新图书的状态，释放图书
        book = self.book_repo.get_by_isbn(borrow.book_isbn)
        if book:
            book.is_borrowed = False
            book.borrowed_by = None
            self.book_repo.save(book)

        # 8. 返回借阅记录
        return ReturnBookDto(
            borrow_id=borrow.id,
            book_isbn=borrow.book_isbn,
            returned_at=now,
            is_overdue=is_overdue,
        )

    def get_my_borrows(
        self, user_id: str, page: int = 1, size: int = 10
    ) -> MyBorrowDto:
        if page < 1:
            page = 1
        if size < 1:
            size = 10
        if size > 100:  # 防止恶意请求
            size = 100
        # total 该用户借阅记录的总数量
        # 返回的元组直接解包，赋值给两个变量
        borrows, total = self.borrow_repo.get_borrows_by_user(user_id, page, size)
        # 客户想在查询的时候直接看到是否已经归还和是否逾期，而数据库中的is_overdue是在还书之后才更新的，所以需要在这里计算
        for borrow in borrows:
            borrow.is_returned = borrow.is_book_returned
            borrow.is_overdue = borrow.is_book_overdue
        pages = (total + size - 1) // size  # 总页数 向上取整

        return MyBorrowDto(
            items=borrows, total=total, page=page, size=size, pages=pages
        )
