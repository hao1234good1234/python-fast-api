from fastapi import APIRouter, Depends, HTTPException
from core.services import  LibraryService
from api.schemas import BorrowRequest, BookResponse, to_book_response, CommonResponse
from api.dependencies import get_library_service, get_current_user
from core.models import User
from infrastructure.database import get_db_session
from sqlalchemy.orm import Session
router = APIRouter() 

@router.post("/", response_model=CommonResponse, summary="借书")
def borrow_book(
    request: BorrowRequest, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db_session),
    service: LibraryService = Depends(get_library_service)): 
    try:
        # 调用业务逻辑借书
        updated_book = service.borrow_book(current_user,request.isbn)
        # 提交事务！（把所有数据库改动真正写入）
        db.commit()
        # 返回成功结果
        return {
            "message": "借阅成功",
            "book": {
                "isbn": updated_book.isbn,
                "title": updated_book.title,
                "author": updated_book.author,
                "is_borrowed": updated_book.is_borrowed,
                "borrowed_by": updated_book.borrowed_by
            }
        }  
    except ValueError as e:
        # 业务错误（比如书不存在、已被借）→ 返回 400
        db.rollback() # ← 出错就回滚，不保存任何改动！
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        # 其他未知错误 → 500
        db.rollback()
        raise HTTPException(status_code=500, detail="服务器内部错误")
    




    
@router.post("/return", response_model=CommonResponse, summary="还书")
def return_book(isbn: str, service: LibraryService = Depends(get_library_service)): 
    try:
        service.return_book(isbn)
        return CommonResponse(message="还书成功")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
# 根据用户 ID 获取所有借阅的图书
@router.get("/user/{user_id}", response_model=list[BookResponse], summary="根据用户 ID 获取所有借阅的图书")
def get_borrows_by_user_id(user_id: str, service: LibraryService = Depends(get_library_service)): 
    books = service.get_borrows_by_user_id(user_id)
    return [to_book_response(b) for b in books]
# 获取所有可以借阅的图书
@router.get("/available", response_model=list[BookResponse], summary="获取所有可以借阅的图书")
def get_available_books(service: LibraryService = Depends(get_library_service)):
    books = service.get_available_books()
    return [to_book_response(b) for b in books]
