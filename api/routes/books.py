from fastapi import APIRouter, Depends, HTTPException
from core.models import Book
from core.services import LibraryService
from api.schemas import BookCreate, to_book_response, BookResponse, CommonResponse
from api.dependencies import get_library_service
# 创建一个“路由容器”，后面所有 `@router.xxx` 的接口都会自动归到这个组里
# 最终在 `main.py` 里会挂到 `/books` 路径下（比如 `app.include_router(books.router, prefix="/books")`）
router = APIRouter() 



@router.post("/", response_model=BookResponse, summary="添加图书")
# `Depends`：FastAPI 的“依赖注入”工具（用来自动获取数据库连接）
#  Depends(get_db_session)`：**自动获取一个数据库连接**, 自动管理数据库连接，你不用操心开/关

def add_book(book: BookCreate, service: LibraryService = Depends(get_library_service)):  # **路由中用 `Depends(get_db_session)`** → 自动注入会话
    # session 会自动传入，且请求结束后自动关闭
    existing = service.get_book_by_isbn(book.isbn)
    if existing:
        raise HTTPException(status_code=400, detail="图书已存在")
    added_book = service.add_book(Book(isbn=book.isbn, title=book.title, author=book.author))
    return to_book_response(added_book)


@router.get("/{isbn}", response_model=BookResponse,summary="根据 ISBN 获取图书")
def get_book(isbn: str, service: LibraryService = Depends(get_library_service)):
    book = service.get_book_by_isbn(isbn)
    if not book:
        raise HTTPException(status_code=404, detail="图书不存在")
    return to_book_response(book)
@router.get("/", response_model=list[BookResponse], summary="获取所有图书")
def list_books(service: LibraryService = Depends(get_library_service)):
    return [to_book_response(book) for book in service.get_all_books()]

@router.put("/", response_model=BookResponse, summary="更新图书")
def update_book(book: BookCreate, service: LibraryService = Depends(get_library_service)):
    existing = service.get_book_by_isbn(book.isbn)
    if not existing:
        raise HTTPException(status_code=404, detail="图书不存在")
    updated_book = service.update_book(Book(isbn=book.isbn, title=book.title, author=book.author))
    return to_book_response(updated_book)

@router.delete("/{isbn}", response_model=CommonResponse, summary="删除图书")
def delete_book(isbn: str, service: LibraryService = Depends(get_library_service)):
    try:
        service.delete_book(isbn)
        return CommonResponse(message="图书删除成功")
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e)) #str(e)返回错误信息