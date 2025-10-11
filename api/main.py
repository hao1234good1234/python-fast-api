import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler()],
    force=True
)

from fastapi import FastAPI, HTTPException
from core.services import LibraryService
from core.models import Book
from infrastructure.json_repos import JsonUserRepo, JsonBookRepo

app = FastAPI(title="Library API", version="1.0.0")
# 初始化服务（这里你可以注入真实的 JSON Repository）
book_repo = JsonBookRepo()  # 从本地文件加载图书数据
user_repo = JsonUserRepo()  # 从本地文件加载用户数据
library_service = LibraryService(book_repo, user_repo)

# FastAPI 在路由匹配时，会优先匹配静态路径（如 /books/list），再匹配动态路径（如 /books/{isbn}）。
# 调整顺序：把静态路径写在动态路径前面
@app.get("/books/list", response_model=list[Book])  # 获取所有图书
def get_all_books():
    books = library_service.get_all_books()
    return books

@app.post("/books/add", response_model=Book)  # 添加图书
def add_book(isbn: str, title: str, author: str) -> Book:
    if not all([isbn, title, author]):
        raise HTTPException(status_code=400, detail="图书信息不能为空")
    return library_service.add_book(isbn, title, author)


@app.get("/books/{isbn}", response_model=Book)  # 获取图书
def get_book(isbn: str):
    book = library_service.get_book_by_isbn(isbn)
    if not book:
        raise HTTPException(status_code=404, detail="图书不存在")
    return book


@app.post("/books/{isbn}/borrow")  # 借阅图书
def borrow_book(isbn: str, user_id: str):
    success = library_service.borrow_book(isbn, user_id)
    if not success:
        raise HTTPException(status_code=400, detail="借阅失败")
    return {"message": "借阅成功"}


@app.post("/books/{isbn}/return")  # 还书
def return_book(isbn: str):
    success = library_service.return_book(isbn)
    if not success:
        raise HTTPException(status_code=400, detail="还书失败")
    return {"message": "还书成功"}


@app.get("/users/{user_id}/books", response_model=list[Book])  # 获取用户借阅的图书
def get_user_books(user_id: str):
    books = library_service.get_user_books(user_id)
    return books

# 启动项目
# uvicorn main:app --reload
# 修改端口
# uvicorn main:app --reload --port=8001