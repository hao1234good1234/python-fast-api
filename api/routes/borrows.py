from fastapi import APIRouter, Depends, Query, BackgroundTasks
from core.services import BorrowService
from api.schemas import SuccessResponse, MyBorrowsResponse, BookBorrowResponse
from api.dependencies import get_current_user, get_borrow_service, get_db
from core.models import User
from sqlalchemy.orm import Session
import logging
from utils.log_borrow_utils import log_borrow_event, log_borrow_to_db
from utils.email_utils import send_email_163
from tasks.tasks import send_email_task

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/books/{isbn}/borrow", response_model=BookBorrowResponse, summary="借书")
def borrow_book(
    isbn: str,
    background_tasks: BackgroundTasks,  # ← 注入 BackgroundTasks,FastAPI 自动注入，无需手动创建
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),  # ← 自动从 request.state.db 拿
    service: BorrowService = Depends(get_borrow_service),
):
    # 调用业务逻辑借书
    result = service.borrow_book(isbn, current_user.user_id)

     # 异步任务实现日志记录: 将日志存到日志文件中
     # ✅ 触发后台任务：记录日志
    background_tasks.add_task(
        log_borrow_event,
        user_id = result.borrower_id,
        book_id = result.book_isbn,
        borrow_id = result.borrow_id   
        
    )

    # 异步任务实现日志记录: 将日志存到数据库audit_logs表中
    # ✅ 触发后台任务：记录日志到数据库
    background_tasks.add_task(
        log_borrow_to_db,
        user_id = result.borrower_id,
        book_id = result.book_isbn,
        borrow_id = result.borrow_id   
        
    )

    # 异步任务实现发送163邮件
    email =current_user.email
    if email:
        # 异步任务实现发送163邮件
        # `.delay()` 是 Celery 提供的方法，用来“立即提交”任务到队列，不等待执行。
        # `.delay()` 是 `apply_async()` 的快捷方式，用于**异步提交任务**
        # 返回的是 `AsyncResult` 对象，包含 `task_id`，可用于后续查询状态。
        # 当你调用 `task.delay()` 时，返回的是一个 `AsyncResult` 对象：
        # 它是一个**异步任务的“代理”或“句柄”**，让你可以在任务执行期间或之后查询其状态和结果。
        task = send_email_task.delay(
            to_email=email,
            subject="图书借阅通知",
            body=f"你好 {current_user.name}，你已成功借阅 ISBN: {result.book_isbn} 的图书。"
        ) 
        print("邮件异步任务已经发送，Task ID:", task.id)
    # 返回成功结果
    return BookBorrowResponse(
        borrow_id=result.borrow_id,
        book_isbn=result.book_isbn,
        borrower_id=result.borrower_id,
        borrowed_at=result.borrowed_at,
        due_date=result.due_date,
        task_id=task.id
    )


# patch请求，局部更新，只更新归还相关的字段
# `get_current_user` 负责 401，`service` 负责 403。
@router.patch("/{borrow_id}/return", response_model=SuccessResponse, summary="还书")
def return_book(
    borrow_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    service: BorrowService = Depends(get_borrow_service),
    db: Session = Depends(get_db),
):
    result = service.return_book(borrow_id, current_user.user_id)
    # 异步任务实现发送163邮件
    email =current_user.email
    if email:
        background_tasks.add_task(
            send_email_163,
            to_email=current_user.email, 
            subject="图书还书通知",
            body=f"你好 {current_user.name}，你已成功归还 ISBN: {result.book_isbn} 的图书。"

        )

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
