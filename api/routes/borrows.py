from fastapi import APIRouter, Depends, HTTPException, Query
from core.services import BorrowService
from api.schemas import ReturnBookResponse, BorrowBookResponse, MyBorrowsResponse
from api.dependencies import get_current_user, get_borrow_service
from core.models import User
from infrastructure.database import get_db_session
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/books/{isbn}/borrow", response_model=BorrowBookResponse, summary="借书")
def borrow_book(
    isbn: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
    service: BorrowService = Depends(get_borrow_service),
):
    try:
        # 调用业务逻辑借书
        result = service.borrow_book(isbn, current_user.user_id)
        # 提交事务！（把所有数据库改动真正写入）
        db.commit()
        # 返回成功结果
        return BorrowBookResponse(
            borrow_id=result.borrow_id,
            book_isbn=result.book_isbn,
            borrower_id=result.borrower_id,
            borrowed_at=result.borrowed_at,
            due_date=result.due_date,
            message="借书成功",
        )
    except ValueError as e:
        # 业务错误（比如书不存在、已被借）→ 返回 400
        db.rollback()  # ← 出错就回滚，不保存任何改动！
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        # 其他未知错误 → 500
        db.rollback()
        raise HTTPException(status_code=500, detail="服务器内部错误")


# patch请求，局部更新，只更新归还相关的字段
@router.patch("/{borrow_id}/return", response_model=ReturnBookResponse, summary="还书")
def return_book(
    borrow_id: int,
    current_user: User = Depends(get_current_user),
    service: BorrowService = Depends(get_borrow_service),
    db: Session = Depends(get_db_session),
):
    try:
        result = service.return_book(borrow_id, current_user.user_id)
        db.commit()
        return ReturnBookResponse(
            borrow_id=result.borrow_id,
            book_isbn=result.book_isbn,
            returned_at=result.returned_at,
            is_overdue=result.is_overdue,
            message="还书成功",
        )
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        logger.exception(e)
        raise HTTPException(status_code=500, detail="还书时发生内部错误")

# ✅ 使用 `Query(...)` 做参数校验：`page >= 1`, `1 <= size <= 100`
@router.get("/me", response_model=MyBorrowsResponse, summary="查询我的借阅记录")
def get_my_borrows(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页记录数"),
    current_user: User = Depends(get_current_user),
    service: BorrowService = Depends(get_borrow_service),
):
    return service.get_my_borrows(current_user.user_id, page, size)
