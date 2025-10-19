from sqlalchemy.orm import Session  # SQLAlchemy 的数据库会话
from .models import BookDB  # ORM 模型（对应数据库表）
from core.models import Book  # 业务模型（纯 Python 对象，不含数据库细节）
from core.interfaces import BookRepository


# 定义一个“书本仓库”类，专门负责和数据库打交道
    # 构造函数：每次创建这个类时，必须传入一个数据库会话（session）
class SqlAlchemyBookRepository(BookRepository):
    def __init__(self, session: Session):
        self._session = session  # 把数据库会话保存到实例变量中，后面 CRUD 都要用它

    # ───────────────────────────────
    # R: Read（根据 ISBN 查询一本书）
    # ───────────────────────────────
    def get_by_isbn(self, isbn: str) -> Book | None:
        """
        功能：根据 ISBN 查找一本书
        参数：isbn - 书的 ISBN 编号（字符串）
        返回：找到的 Book 对象，或 None（如果没找到）
        """
        # 1.  从数据库查 BookDB 对象： books 表中找 isbn 等于传入值的记录
        #    .first() 表示只取第一条（因为 ISBN 是主键，最多只有一条）
        db_book = self._session.query(BookDB).filter(BookDB.isbn == isbn).first()

        # 2. 转换成领域模型 Book（核心！解耦数据库和业务）；否则返回 None
        return self._to_domain(db_book) if db_book else None

    # ───────────────────────────────
    # R: Read All（获取所有书）
    # ───────────────────────────────
    def get_all(self) -> list[Book]:
        """
        功能：获取数据库中所有的书
        返回：Book 对象列表
        """
        # 1. 查询所有 BookDB 记录
        db_books = self._session.query(BookDB).all()
        # 2. 把每个 ORM 对象都转成业务对象，组成列表返回
        return [self._to_domain(db_book) for db_book in db_books]

    # ───────────────────────────────
    # U: save（insert or update一本书）
    # ───────────────────────────────
    def save(self, book: Book) -> None:
        """
        功能：更新已存在的书（根据 ISBN 匹配）
        参数：book - 包含最新信息的 Book 对象
        返回：更新后的 Book 对象
        """
        # 1. 先根据 ISBN 找到数据库中的记录
        db_book = self._session.query(BookDB).filter(BookDB.isbn == book.isbn).first()
        # 如果没找到，新建一条，这里是新增逻辑
        if not db_book:
            db_book = BookDB(
                isbn=book.isbn,
                title=book.title,
                author=book.author
            )
            self._session.add(db_book)
        # 2. 更新状态（不管新旧，都同步 is_borrowed 和 borrowed_by）
        else:
            db_book.title = book.title
            db_book.author = book.author
            db_book.is_borrowed = book.is_borrowed
            db_book.borrowed_by = book.borrowed_by

       # 注意：这里不 commit！由 API 层统一提交（保证事务）
    #    ✅ 重点：**Repository 负责“数据库 ↔ 领域模型”转换**，业务代码永远看不到 SQLAlchemy！

    # ───────────────────────────────
    # D: Delete（删除一本书）
    # ───────────────────────────────
    def delete(self, isbn: str) -> bool:
        """
        功能：根据 ISBN 删除一本书
        参数：isbn - 要删除的书的 ISBN
        返回：True 表示删除成功，False 表示书不存在
        """
        # 1. 查找要删除的书
        db_book = self._session.query(BookDB).filter(BookDB.isbn == isbn).first()
        # 2. 如果找到了，就删除它
        if db_book:
            # 标记为删除
            self._session.delete(db_book)
            # 注意：这里不 commit！由 API 层统一提交（保证事务）
            return True
        return False

    # ───────────────────────────────
    # 查询：获取已借阅的图书
    # ───────────────────────────────
    def get_borrows_by_user(self, user_id: str) -> list[Book]:
        # ✅ SQLAlchemy ORM 写法（自动参数化）
        db_books = (
            self._session.query(BookDB)
            .filter(BookDB.borrowed_by == user_id, BookDB.is_borrowed == True)
            .all()
        )
        return [self._to_domain(db_book) for db_book in db_books]

    # ───────────────────────────────
    # 查询：获取所有可借阅的图书
    # ───────────────────────────────
    def get_all_available(self) -> list[Book]:
        db_books = self._session.query(BookDB).filter(BookDB.is_borrowed == False).all()
        return [self._to_domain(db_book) for db_book in db_books]

    # ───────────────────────────────
    # 辅助方法：ORM 模型 → 业务模型
    # ───────────────────────────────
    def _to_domain(self, db_book: BookDB) -> Book:
        """
        功能：把数据库对象（BookDB）转换成业务对象（Book）
        为什么需要？因为业务层不应该知道数据库细节！
        """
        return Book(
            isbn=db_book.isbn,
            title=db_book.title,
            author=db_book.author,
            is_borrowed=db_book.is_borrowed,
            borrowed_by=db_book.borrowed_by
        )
