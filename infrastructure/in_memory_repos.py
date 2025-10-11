# 💾 第四步：实现内存存储（`infrastructure/in_memory_repos.py`）
from core.models import Book, User
import logging

logger = logging.getLogger(__name__)


# 鸭子类型 + Protocol
class InMemoryBookRepo:
    # 实现 BookRepository 协议
    def __init__(self):
        self._books = {}  # 属性的字典格式是{isbn: Book}

    def get_by_isbn(self, isbn: str) -> Book | None:
        return self._books.get(isbn)

    def save(self, book: Book) -> None:
        logger.info(f"保存图书 {book.title}")
        self._books[book.isbn] = (
            book  # 借书还书都要保存，放到_books里，key是isbn，不会重复
        )

    def list_all(self) -> list[Book]:
        return list(self._books.values())


class InMemoryUserRepo:
    # 实现 UserRepository 协议
    def __init__(self):
        self._users = {}  # 属性的字典格式是{user_id: User}

    def get_by_id(self, user_id: str) -> User | None:
        return self._users.get(user_id)

    def save(self, user: User) -> None:
        logger.info(f"保存用户 {user.name}")
        self._users[user.user_id] = user


# ✅ 未来想换数据库？只需重写这个文件，**core 完全不用动！**

# ← 保留（用于测试）
