import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler()],
    force=True,
)

from fastapi import FastAPI, HTTPException
from core.services import LibraryService
from core.models import Book
from infrastructure.json_repos import JsonUserRepo, JsonBookRepo
from api.schemas import (
    BookCreate,
    BookResponse,
    to_book_response,
    BookSummary,
    BookDetail,
    UserPublic,
)

app = FastAPI(
    title="图书馆管理系统",
    description="""
    一个简单的图书借阅系统，支持：
    - 添加图书
    - 查询图书（按作者等）
    - 借书/还书
    - 用户管理

    所有数据默认存储在 `data/` 目录的 JSON 文件中。
    """,
    version="1.0.0",
    contact={"name": "会吃的橘子", "email": "dev@example.com"},
    openapi_tags=[
        {"name": "图书管理", "description": "图书的增删改查、借阅状态管理"},
        {"name": "用户管理", "description": "用户注册、信息查询"},
    ],
)

# 初始化服务（这里你可以注入真实的 JSON Repository）
book_repo = JsonBookRepo()  # 从本地文件加载图书数据
user_repo = JsonUserRepo()  # 从本地文件加载用户数据
library_service = LibraryService(book_repo, user_repo)


# FastAPI 在路由匹配时，会优先匹配静态路径（如 /books/list），再匹配动态路径（如 /books/{isbn}）。
# 调整顺序：把静态路径写在动态路径前面
@app.get(
    "/books/list",
    response_model=list[BookSummary],
    summary="获取所有图书",  # ← 简短摘要（显示在列表中）
    description="获取所有图书，可选参数：\n- `author`：按作者精确匹配\n- `title`：按书名模糊匹配（不区分大小写）",  # ← 详细描述
    tags=["图书管理"],  # 接口分组
)
# 列表页要精简（不返回借阅人），详情页要完整	✅ 需要两个模型
def get_all_books(
    author: str | None = None, title: str | None = None
) -> list[BookSummary]:
    """
    获取所有图书
    参数：
        author: 作者（可选，精确匹配）
        title: 书名（可选，模糊匹配，不区分大小写）
    返回值：
        list[BookResponse]：图书列表
    """
    books = library_service.get_all_books()
    # 应用过滤条件
    filtered_books = books
    if author is not None:
        filtered_books = [book for book in filtered_books if book.author == author]
    if title is not None:
        filtered_books = [
            book for book in filtered_books if title.lower() in book.title.lower()
        ]  # 根据书名模糊匹配
    # 💡 `model_validate()` 是 Pydantic v2 的方法，能安全地从任意对象创建模型实例。
    return [BookSummary.model_validate(book) for book in filtered_books]


# @app.post("/books/add",  response_model=Book, deprecated=True)  # ← Swagger 会显示“已废弃”
# @app.post("/books/add", response_model=Book, include_in_schema=False)  # 隐藏某些接口（比如内部调试用）# 这个接口不会出现在 /docs 或 /redoc 中


# - **GET** 用查询参数（安全、幂等）
# - **POST/PUT** 用 JSON 请求体（数据量大、结构复杂、更安全）
# 给每个接口添加描述和示例
@app.post(
    "/books",
    response_model=BookResponse,
    summary="添加图书",  # ← 简短摘要（显示在列表中）
    description="添加一本新书需要提供：\n- `isbn`：图书的国际标准书号\n- `title`：图书名称\n- `author`：图书作者",  # ← 详细描述
    tags=["图书管理"],  # 接口分组
)
def add_book(book: BookCreate) -> BookResponse:  # ← 直接接收 JSON
    """
    添加图书
    参数:
    book: BookRequest
    返回值:
    Book
    """
    if not all([book.isbn.strip(), book.title.strip(), book.author.strip()]):
        raise HTTPException(status_code=400, detail="图书信息不能为空")
    book = library_service.add_book(book.isbn, book.title, book.author)
    return to_book_response(book)


@app.get(
    "/books/{isbn}",
    response_model=BookDetail,
    summary="根据 ISBN 获取图书",
    description="根据 ISBN 获取图书：\n- `isbn`：图书的国际标准书号",
    tags=["图书管理"],
)
# 列表页要精简（不返回借阅人），详情页要完整	✅ 需要两个模型
def get_book(isbn: str) -> BookDetail:
    book = library_service.get_book_by_isbn(isbn)
    if not book:
        raise HTTPException(status_code=404, detail="图书不存在")
    return BookDetail.model_validate(book)


@app.post(
    "/books/{isbn}/borrow",
    response_model=dict,
    summary="借阅图书",
    description="借阅图书：\n- `isbn`：图书的国际标准书号\n- `user_id`：用户的 ID",
    tags=["图书管理"],
)  # 借阅图书
def borrow_book(isbn: str, user_id: str):
    success = library_service.borrow_book(isbn, user_id)
    if not success:
        raise HTTPException(status_code=400, detail="借阅失败")
    return {"message": "借阅成功"}


@app.post(
    "/books/{isbn}/return",
    response_model=dict,
    summary="还书",
    description="还书：\n- `isbn`：图书的国际标准书号",
    tags=["图书管理"],
)  # 还书
def return_book(isbn: str):
    success = library_service.return_book(isbn)
    if not success:
        raise HTTPException(status_code=400, detail="还书失败")
    return {"message": "还书成功"}


@app.get(
    "/users/{user_id}/books",
    response_model=list[BookResponse],
    summary="获取用户借阅的图书",
    description="获取用户借阅的图书：\n- `user_id`：用户的 ID",
    tags=["图书管理"],
)  # 获取用户借阅的图书
def get_user_books(user_id: str) -> list[BookResponse]:
    books = library_service.get_user_books(user_id)
    return [to_book_response(b) for b in books]


# ✅ **神奇之处**：只要字段名和类型匹配，FastAPI 会自动把 `dataclass` / `dict` / `ORM model` 转成 Pydantic 模型！
# ← 即使返回的是 Book(dataclass)，FastAPI 会自动转成 BookResponse！
# 现在User和UserPublic的字段不一样，不能自动转换！需要手动转换：UserPublic(user_id=user.user_id, name=user.name)


@app.get(
    "/users/{user_id}",
    response_model=UserPublic,
    summary="获取用户信息",
    description="获取用户信息：\n- `user_id`：用户的 ID",
    tags=["用户管理"],
)
def get_user(user_id: str) -> UserPublic:
    user = user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return UserPublic(user_id=user.user_id, name=user.name)


# 启动项目
# uvicorn main:app --reload
# 修改端口
# uvicorn main:app --reload --port=8001
