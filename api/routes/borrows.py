from fastapi import APIRouter, Depends, Query
from core.services import BorrowService
from api.schemas import SuccessResponse, MyBorrowsResponse
from api.dependencies import get_current_user, get_borrow_service, get_db
from core.models import User
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/books/{isbn}/borrow", response_model=SuccessResponse, summary="借书")
def borrow_book(
    isbn: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),  # ← 自动从 request.state.db 拿
    service: BorrowService = Depends(get_borrow_service),
):
    # 调用业务逻辑借书
    result = service.borrow_book(isbn, current_user.user_id)
    # 返回成功结果
    return SuccessResponse(message="借书成功", data=result)
    


# patch请求，局部更新，只更新归还相关的字段
# `get_current_user` 负责 401，`service` 负责 403。
@router.patch("/{borrow_id}/return", response_model=SuccessResponse, summary="还书")
def return_book(
    borrow_id: int,
    current_user: User = Depends(get_current_user),
    service: BorrowService = Depends(get_borrow_service),
    db: Session = Depends(get_db),
):
    result = service.return_book(borrow_id, current_user.user_id)
    return SuccessResponse(message="还书成功", data=result)

# ✅ 使用 `Query(...)` 做参数校验：`page >= 1`, `1 <= size <= 100`
@router.get("/me", response_model=MyBorrowsResponse, summary="查询我的借阅记录")
def get_my_borrows(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页记录数"),
    current_user: User = Depends(get_current_user),
    service: BorrowService = Depends(get_borrow_service),
):
    return service.get_my_borrows(current_user.user_id, page, size)
