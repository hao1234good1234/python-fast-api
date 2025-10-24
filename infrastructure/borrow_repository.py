from sqlalchemy.orm import Session
from core.interfaces import BorrowRepository
from core.models import BorrowRecord
from .models import BorrowRecordDB, BookDB
from core.dtos import BorrowRecordDto
from datetime import datetime, timezone


class SqlAlchemyBorrowRepository(BorrowRepository):
    def __init__(self, session: Session):
        self._session = session


    def create(self, borrow: BorrowRecord) -> BorrowRecord:
        """专门用于创建新借阅记录"""
        db_borrow = BorrowRecordDB(
            book_isbn = borrow.book_isbn,
            borrower_id = borrow.borrower_id,
            borrowed_at = borrow.borrowed_at,
            due_date = borrow.due_date
          # 其他字段用默认值（returned_at=None, is_returned=False...）

        )
        self._session.add(db_borrow)
        self._session.flush()   # 立即获取生成的 ID，但不 commit
        return self._to_domain(db_borrow)

    def get_by_id(self, borrow_id: int) -> BorrowRecord | None:
        db_borrow = (
            self._session.query(BorrowRecordDB)
            .filter(BorrowRecordDB.id == borrow_id)
            .first()
        )
        return self._to_domain(db_borrow) if db_borrow else None
    
    def save(self, borrow: BorrowRecord) -> None: 
        db_borrow= self._session.query(BorrowRecordDB).filter(BorrowRecordDB.id == borrow.id).one() # 必须存在

        db_borrow.returned_at = borrow.returned_at
        db_borrow.is_returned = borrow.is_returned
        db_borrow.is_overdue = borrow.is_overdue



    def get_borrows_by_user(self, 
                            user_id: str,
                            page: int = 1,
                            size: int = 10
) -> tuple[list[BorrowRecordDto], int]: # 返回借阅记录和总数量
        """
        分页查询用户的借阅记录（含书名）
        返回: (记录列表, 总数量)
        """
        offset = (page - 1) * size

        # 查询该用户借阅记录的总数量，用于分页
        total = self._session.query(BorrowRecordDB).filter(BorrowRecordDB.borrower_id == user_id).count()

        # 查询借阅激励，并关联join图书表查询出书名
        # ✅ 使用 `JOIN` 一次查出借阅记录 + 书名，避免 N+1 查询。
        query=(
            self._session
            .query(BorrowRecordDB, BookDB.title)
            .join(BookDB, BorrowRecordDB.book_isbn == BookDB.isbn)
            .filter(BorrowRecordDB.borrower_id == user_id)
            .order_by(BorrowRecordDB.borrowed_at.desc()) # 按借阅时间降序排序
            .offset(offset)
            .limit(size)
        )
        result = []
        for db_borrow, book_title in query.all():
            result.append(self._to_domain_with_title(db_borrow, book_title))
        return result, total
    
    
    def _to_domain_with_title(self, db_borrow: BorrowRecordDB, book_title: str) -> BorrowRecordDto:
        due_date = db_borrow.due_date
        returned_at = db_borrow.returned_at
        if due_date.tzinfo is None:
            dute_date = due_date.replace(tzinfo=timezone.utc)
        if returned_at is not None:
            if returned_at.tzinfo is None:
                returned_at = returned_at.replace(tzinfo=timezone.utc)
        return BorrowRecordDto(
            id=db_borrow.id,
            book_isbn=db_borrow.book_isbn,
            book_title=book_title,
            borrower_id=db_borrow.borrower_id,
            borrowed_at=db_borrow.borrowed_at,
            due_date=dute_date,
            returned_at=returned_at,
            is_returned=db_borrow.is_returned,
            is_overdue=db_borrow.is_overdue,
        )


    def _to_domain(self, db_borrow: BorrowRecordDB) -> BorrowRecord:
        due_date = db_borrow.due_date
        if due_date.tzinfo is None:
            due_date = due_date.replace(tzinfo=timezone.utc)
        return BorrowRecord(
            id=db_borrow.id,
            book_isbn=db_borrow.book_isbn,
            borrower_id=db_borrow.borrower_id,
            borrowed_at=db_borrow.borrowed_at,
            due_date=due_date,
            returned_at=db_borrow.returned_at,
            is_returned=db_borrow.is_returned,
            is_overdue=db_borrow.is_overdue
        )
    
# ✅ 注意：`save` 方法同样 **不 commit**，由上层控制事务。
