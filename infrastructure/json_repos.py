# ✅ 新增：JSON 持久化实现
import json

# import os
from pathlib import Path
from core.models import User, Book
# from core.interfaces import UserRepository, BookRepository

# E:\Projects\vscode\python-demo\library_system\data
# 将数据文件放在项目根目录library_system\data
_CURRENT_DIR = Path(__file__).parent
PROJECT_ROOT = _CURRENT_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
BOOKS_FILE = DATA_DIR / "books.json"
USERS_FILE = DATA_DIR / "users.json"

# 确保目录存在
DATA_DIR.mkdir(exist_ok=True)


# 从文件加载数据
def _load_json(file_path: Path, default: dict) -> dict:
    if not file_path.exists():
        return default
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


# 保存数据
def _save_json(file_path: Path, data: dict) -> None:
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# JSON 持久化实现
class JsonBookRepo:
    def __init__(self):
        self._load_books()

    def _load_books(self):
        raw_books = _load_json(BOOKS_FILE, {})  # 从本地文件加载json数据
        self._books = {
            isbn: Book(**book) for isbn, book in raw_books.items()
        }  # 将本地的json数据转换成Book对象

    def _save_books(self):
        raw_books = {
            isbn: book.__dict__ for isbn, book in self._books.items()
        }  # 将Book对象转换成json数据
        _save_json(BOOKS_FILE, raw_books)  # 将json数据保存到本地文件

    # 下面三个方法：BookRepository的实现：鸭子类型 + Protocol
    def get_by_isbn(self, isbn: str) -> Book | None:
        return self._books.get(isbn)

    def save(self, book: Book) -> None:
        self._books[book.isbn] = (
            book  # 借书还书都要保存，放到_books里，key是isbn，不会重复
        )
        self._save_books()  # 每次保存都要将最新的数据保存到本地文件

    def list_all(self) -> list[Book]:
        return list(self._books.values())  # 获取所有图书


class JsonUserRepo:
    def __init__(self):
        self._load_users()

    def _load_users(self):
        raw_users = _load_json(USERS_FILE, {})
        self._users = {user_id: User(**user) for user_id, user in raw_users.items()}

    def _save_users(self):
        raw_users = {user_id: user.__dict__ for user_id, user in self._users.items()}
        _save_json(USERS_FILE, raw_users)

    # 下面两个方法：UserRepository的实现：鸭子类型 + Protocol
    def get_by_id(self, user_id: str) -> User | None:
        return self._users.get(user_id)

    def save(self, user: User) -> None:
        self._users[user.user_id] = user  # key是user_id，不会重复
        self._save_users()  # 每次保存都要将最新的数据保存到本地文件


# ✅ 这个实现 **完全满足 `BookRepository` 和 `UserRepository` 协议**，但数据存在 JSON 文件中！
