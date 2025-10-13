from sqlalchemy.orm import Session  # SQLAlchemy 的数据库会话
from database.models import BookDB  # ORM 模型（对应数据库表）
from core.models import Book  # 业务模型（纯 Python 对象，不含数据库细节）


# 定义一个“书本仓库”类，专门负责和数据库打交道
class SqlAlchemyBookRepository:
    # 构造函数：每次创建这个类时，必须传入一个数据库会话（session）
    def __init__(self, session: Session):
        self._session = session  # 把数据库会话保存到实例变量中，后面 CRUD 都要用它

    # ───────────────────────────────
    # C: Create（创建一本书）
    # ───────────────────────────────
    def create(self, book: Book) -> Book:
        """
        功能：把一个“业务书本对象”存入数据库
        参数：book - 一个 core.models.Book 对象（比如 Book(isbn="123", title="Python入门")）
        返回：存入数据库后的 Book 对象（可能包含数据库生成的默认值）
        """
        # 1. 把业务模型（Book）转换成 ORM 模型（BookDB）
        db_book = BookDB(
            isbn=book.isbn,
            title=book.title,
            author=book.author,
            is_borrowed=book.is_borrowed,
            borrowed_by=book.borrowed_by,
        )
        # 2. 告诉 SQLAlchemy：“我要把这个对象加到数据库里”
        self._session.add(db_book)
        # 3. 真正执行 SQL 插入语句（提交事务）
        self._session.commit()
        # 4. 刷新对象：从数据库读回最新数据（比如如果有默认值、自增ID等）
        self._session.refresh(db_book)  # 获取数据库生成的值（如默认值）
        # 5. 把 ORM 模型转回业务模型，返回给调用者
        return self._to_domain(db_book)

    # ───────────────────────────────
    # R: Read（根据 ISBN 查询一本书）
    # ───────────────────────────────
    def get_by_isbn(self, isbn: str) -> Book | None:
        """
        功能：根据 ISBN 查找一本书
        参数：isbn - 书的 ISBN 编号（字符串）
        返回：找到的 Book 对象，或 None（如果没找到）
        """
        # 1. 查询数据库：从 books 表中找 isbn 等于传入值的记录
        #    .first() 表示只取第一条（因为 ISBN 是主键，最多只有一条）
        db_book = self._session.query(BookDB).filter(BookDB.isbn == isbn).first()

        # 2. 如果找到了，就转成业务模型返回；否则返回 None
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
    # U: Update（更新一本书）
    # ───────────────────────────────
    def update(self, book: Book) -> Book:
        """
        功能：更新已存在的书（根据 ISBN 匹配）
        参数：book - 包含最新信息的 Book 对象
        返回：更新后的 Book 对象
        """
        # 1. 先根据 ISBN 找到数据库中的记录
        db_book = self._session.query(BookDB).filter(BookDB.isbn == book.isbn).first()
        # 2. 如果没找到，抛出错误
        if not db_book:
            raise ValueError(f"ISBN 为 {book.isbn} 的书不存在，无法更新！")
        # 3. 更新字段（SQLAlchemy 会自动跟踪变化）
        db_book.title = book.title
        db_book.author = book.author
        db_book.is_borrowed = book.is_borrowed
        db_book.borrowed_by = book.borrowed_by
        # 4. 提交更改到数据库
        self._session.commit()
        # 5. 刷新并返回
        self._session.refresh(db_book)  # 获取数据库生成的值（如默认值）
        return self._to_domain(db_book)

    # ───────────────────────────────
    # D: Delete（删除一本书）
    # ───────────────────────────────
    def delete(self, isbn: str) -> None:
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
            # 真正执行 DELETE 语句
            self._session.commit()
            return True
        return False

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
            borrowed_by=db_book.borrowed_by,
        )
