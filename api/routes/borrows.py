from fastapi import APIRouter, Depends, HTTPException
from core.services import BorrowService
from api.schemas import BorrowRequest, BookResponse, to_book_response, CommonResponse
from api.dependencies import get_borrow_service
router = APIRouter() 

@router.post("/", response_model=CommonResponse, summary="借书")
def borrow_book(request: BorrowRequest, service: BorrowService = Depends(get_borrow_service)): 
    try:
        borrowed_book = service.borrow_book(request.user_id, request.isbn)
        return CommonResponse(message=f"用户 {request.user_id} 借阅了图书 {borrowed_book.title}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/return", response_model=CommonResponse, summary="还书")
def return_book(isbn: str, service: BorrowService = Depends(get_borrow_service)): 
    try:
        returned_book = service.return_book(isbn)
        return CommonResponse(message=f"图书 {returned_book.title} 已归还")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
# 根据用户 ID 获取所有借阅的图书
@router.get("/user/{user_id}", response_model=list[BookResponse], summary="根据用户 ID 获取所有借阅的图书")
def get_borrows_by_user_id(user_id: str, service: BorrowService = Depends(get_borrow_service)): 
    books = service.get_borrows_by_user_id(user_id)
    return [to_book_response(b) for b in books]
# 获取所有可以借阅的图书
@router.get("/available", response_model=list[BookResponse], summary="获取所有可以借阅的图书")
def get_available_books(service: BorrowService = Depends(get_borrow_service)):
    books = service.get_available_books()
    return [to_book_response(b) for b in books]
