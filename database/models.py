#  第四步：定义 ORM 模型（`database/models.py`）
# SQLAlchemy 模型
from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

# 4. 声明基类（用于定义模型）
Base = declarative_base()

class BookDB(Base):
    __tablename__ = "books"
    isbn = Column(String, primary_key=True, index= True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    is_borrowed= Column(Boolean, default=False, nullable=False)
    borrowed_by = Column(String, ForeignKey("users.user_id"), nullable=True)

class UserDB(Base):
    __tablename__ = "users"
    user_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)

#  注意：这是 **数据库模型**，和你 `core/models.py` 中的 `Book`、`User`（业务模型）是分开的！
