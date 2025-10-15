#  第四步：定义 ORM 模型（`database/models.py`）
# SQLAlchemy 模型
from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

# 4. 声明基类（用于定义模型）
Base = declarative_base()


class BookDB(Base):
    __tablename__ = "books"
    isbn = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    is_borrowed = Column(Boolean, default=False, nullable=False)
    borrowed_by = Column(String, ForeignKey("users.user_id"), nullable=True)


class UserDB(Base):
    __tablename__ = "users"
    user_id = Column(String, primary_key=True, index=True)
    name = Column(
        String, nullable=False
    )  # `name` 是用于展示的昵称或真实姓名（可重复、可修改）
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

#  注意：这是 **数据库模型**，和你 `core/models.py` 中的 `Book`、`User`（业务模型）是分开的！
