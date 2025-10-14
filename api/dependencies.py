# `get_library_service` 在多个路由文件中重复定义 改进方案：**统一移到 `api/dependencies.py`**
from sqlalchemy.orm import Session
from fastapi import Depends
from infrastructure.database import get_db_session
from infrastructure.user_repository import SqlAlchemyUserRepository
from infrastructure.book_repository import SqlAlchemyBookRepository
from core.services import LibraryService, BorrowService


def get_library_service(session: Session = Depends(get_db_session)):
    return LibraryService(
        user_repo=SqlAlchemyUserRepository(session),
        book_repo=SqlAlchemyBookRepository(session)
    )


def get_borrow_service(session: Session = Depends(get_db_session)):
    return BorrowService(
        user_repo=SqlAlchemyUserRepository(session),
        book_repo=SqlAlchemyBookRepository(session)
    )
# ✅ 代码复用 + 单一职责 + 易于扩展（比如以后加 `get_audit_service`）