from fastapi import APIRouter, Depends, HTTPException, Path
from core.models import Book
from core.services import LibraryService
from api.schemas import BookCreate, to_book_response, BookResponse, SuccessResponse
from api.dependencies import get_library_service, get_db
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

# 创建一个“路由容器”，后面所有 `@router.xxx` 的接口都会自动归到这个组里
# 最终在 `main.py` 里会挂到 `/books` 路径下（比如 `app.include_router(books.router, prefix="/books")`）
router = APIRouter()


@router.post("/", response_model=SuccessResponse, summary="添加图书")
# `Depends`：FastAPI 的“依赖注入”工具（用来自动获取数据库连接）
#  Depends(get_db_session)`：**自动获取一个数据库连接**, 自动管理数据库连接，你不用操心开/关

def add_book(
    book: BookCreate,
    db: Session = Depends(get_db),
    service: LibraryService = Depends(get_library_service),
):  # **路由中用 `Depends(get_db_session)`** → 自动注入会话
    # session 会自动传入，且请求结束后自动关闭
    service.add_book(Book(isbn=book.isbn, title=book.title, author=book.author))
    return SuccessResponse(message="图书添加成功")


@router.get("/{isbn}", response_model=BookResponse, summary="根据 ISBN 获取图书")
def get_book(isbn: str, service: LibraryService = Depends(get_library_service)):
    book = service.get_book_by_isbn(isbn)
    if not book:
        raise HTTPException(status_code=404, detail="图书不存在")
    return to_book_response(book)


@router.get("/", response_model=list[BookResponse], summary="获取所有图书")
def list_books(service: LibraryService = Depends(get_library_service)):
    return [to_book_response(book) for book in service.get_all_books()]


@router.put(
    "/{isbn}", response_model=BookResponse, summary="更新图书"
)  # ← 补上路径参数（RESTful）
def update_book(
    book_update: BookCreate,  # ← 避免和路径参数 isbn 冲突
    service: LibraryService = Depends(get_library_service),
    db: Session = Depends(get_db),
):
    # 更新字段（保持 ISBN 不变）
    updated_book = Book(
        isbn=book_update.isbn, title=book_update.title, author=book_update.author
    )
    service.update_book(updated_book)
    return to_book_response(updated_book)


@router.delete(
    "/{isbn}",
    summary="删除图书",
    description="""
    根据图书的 ISBN 删除数据库中的记录。
    
    - 如果图书不存在，返回 404 状态码
    - 成功删除后，返回成功消息
    - 该操作不可逆，请谨慎调用
    """,
    response_model=SuccessResponse,
    responses={
        200: {
            "description": "删除成功",
            "content": {
                "application/json": {
                    "example": {
                        "code": 200,
                        "message": "图书删除成功",
                        "data": {"isbn": "999-0134685994"}
                    }
                }
            }
        },
        404: {
            "description": "图书未找到",
            "content": {
                "application/json": {
                    "example": {
                        "code": 404,
                        "message": "图书不存在",
                        "data": None
                    }
                }
            }
        },
        500: {
            "description": "服务器错误",
            "content": {
                "application/json": {
                    "example": {
                        "code": 500,
                        "message": "服务器错误",
                        "data": None
                    }
                }
            }
            
        }
    }
)
def delete_book(
    isbn: str = Path(
        ...,
        description="图书编号，例如： 999-0134685994",
        example="999-0134685994",
    ),
    service: LibraryService = Depends(get_library_service),
    db: Session = Depends(get_db),
):
    deleted = service.delete_book(isbn)
    if not deleted:
        logger.info("图书不存在")
        return SuccessResponse(code="NOT_FOUND", message="图书不存在")
    return SuccessResponse(message="图书删除成功",data={"isbn": isbn})
