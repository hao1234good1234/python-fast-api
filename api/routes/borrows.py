from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.services import BorrowService
from infrastructure.database import get_db_session
from api.schemas import BorrowRequest
router = APIRouter() 



@router.post("/", response_model=dict, summary="借书")
def borrow_book(request: BorrowRequest, session: Session = Depends(get_db_session)): 
    borrowService = BorrowService(session)
    try:
        return borrowService.borrow_book(request.user_id, request.isbn)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/return", response_model=dict, summary="还书")
def return_book(isbn: str, session: Session = Depends(get_db_session)): 
    borrowService = BorrowService(session)
    try:
        return borrowService.return_book(isbn)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

