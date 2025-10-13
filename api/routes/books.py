from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.models import Book
from infrastructure.book_repository import SqlAlchemyBookRepository
from infrastructure.database import get_db_session
# 创建一个“路由容器”，后面所有 `@router.xxx` 的接口都会自动归到这个组里
# 最终在 `main.py` 里会挂到 `/books` 路径下（比如 `app.include_router(books.router, prefix="/books")`）
router = APIRouter() 

@router.post("/", response_model=Book)
# `Depends`：FastAPI 的“依赖注入”工具（用来自动获取数据库连接）
#  Depends(get_db_session)`：**自动获取一个数据库连接**, 自动管理数据库连接，你不用操心开/关

def add_book(book: Book, session: Session = Depends(get_db_session)): 
    repo = SqlAlchemyBookRepository(session)
    existing = repo.get_by_isbn(book.isbn)
    if existing:
        raise HTTPException(status_code=400, detail="图书已存在")
    return repo.create(book)


@router.get("/{isbn}", response_model=Book)
def get_book(isbn: str, session: Session = Depends(get_db_session)):
    repo = SqlAlchemyBookRepository(session)
    book = repo.get_by_isbn(isbn)
    if not book:
        raise HTTPException(status_code=404, detail="图书不存在")
    return book
@router.get("/", response_model=list[Book])
def list_books(session: Session = Depends(get_db_session)):
    repo = SqlAlchemyBookRepository(session)
    return repo.get_all()