#  第四步：定义 ORM 模型（`database/models.py`）
# SQLAlchemy 模型
from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, Integer, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone

# 4. 声明基类（用于定义模型）
Base = declarative_base()


#  注意：这是 **数据库模型**，和你 `core/models.py` 中的 `Book`、`User`（业务模型）是分开的！


class BookDB(Base):
    __tablename__ = "books"
    isbn = Column(String, primary_key=True, index=True)  # ISBN 作主键！
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    is_borrowed = Column(Boolean, default=False, nullable=False)  # 是否被借出
    borrowed_by = Column(
        String, ForeignKey("users.user_id"), nullable=True
    )  # 借书人 user_id


class UserDB(Base):
    __tablename__ = "users"
    user_id = Column(String, primary_key=True, index=True)
    name = Column(
        String, nullable=False
    )  # `name` 是用于展示的昵称或真实姓名（可重复、可修改）
    email = Column(String, nullable=False)
    # 新增字段
    username = Column(
        String, unique=True, index=True
    )  # **`username` 是用于登录的身份凭证（唯一、不可变）, 唯一、可索引（加快登录查询）
    hashed_password = Column(String)  # 存哈希值
    # - `is_active = True`：账号正常，可以登录、操作。
    # - `is_active = False`：账号被**禁用/冻结/未激活**，**不能登录或使用系统功能**。
    # 软删除（`is_active=False`）比物理删除更安全、灵活。
    is_active = Column(Boolean, default=True)
    # ⚠️ 注意：**永远不要把 `password` 字段存入数据库或返回给前端！**


class BorrowRecordDB(Base):
    __tablename__ = "borrows"
    id = Column(Integer, primary_key=True, index=True)
    book_isbn = Column(String, ForeignKey("books.isbn"), nullable=False)
    borrower_id = Column(String, nullable=False)  # 借书人 ID（如 "user123"）
    # 数据库存时区，DateTime(timezone=True)
    # - **SQLite**：实际存的是字符串，但 SQLAlchemy 会帮你处理时区
    # - **PostgreSQL**：原生支持 `TIMESTAMP WITH TIME ZONE`，推荐！
    borrowed_at = Column(
        DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc)
    )
    due_date = Column(DateTime(timezone=True), nullable=False)
    returned_at = Column(DateTime(timezone=True), nullable=True)
    is_returned = Column(Boolean, default=False)
    is_overdue = Column(Boolean, default=False)
    #     - 每次借书，**新增一条记录**
    # - `due_date = borrowed_at + 7天`（可配置）
    # - `returned_at` 和 `is_returned` 初始为 `None` / `False`

    # ✅ 图书表 `BookDB` 已有 `is_borrowed` 和 `borrowed_by` 字段。

# 日志表
class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True,index=True)
    action = Column(String(50), nullable=False)   # 例如: "borrow_created", "book_deleted"
    user_id = Column(String, nullable=True)   # 操作人（可为空，如系统任务）
    timestamp = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))  # 记录时间
    details = Column(JSON, nullable=True)  # 存储额外上下文，如 {"book_id": 123}
    ip_address = Column(String(45), nullable=True)     # 可选：记录 IP
    user_agent = Column(Text, nullable=True)  # 可选：浏览器信息

    # 🔸 使用 `JSON` 类型（PostgreSQL/MySQL 5.7+ 支持）可以灵活存储结构化日志内容
    # 🔸 如果用 SQLite，可以用 `Text` 存 JSON 字符串，并在应用层 `json.loads/dumps`

