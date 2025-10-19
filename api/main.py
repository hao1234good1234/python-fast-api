import logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler()],
    force=True,
)
from fastapi import FastAPI
from api.routes import books, users, borrows, auth

from infrastructure.connection import engine
from infrastructure.models import Base
import os
import uvicorn
from api.exception_handlers import register_exception_handlers
from middleware.middleware import DBSessionMiddleware
from settings import settings

# ✅ 第一次运行时，`data/library.db` 会自动创建，表也会生成！
#  Base 不仅是个基类，它还偷偷记住了所有继承它的子类（也就是你的表）！
# create_all() 只创建不存在的表，已有的表完全不动，数据也不会丢。
# 如果没有，就执行 CREATE TABLE ... 语句
# 如果已有，就跳过（不会重复建，也不会删数据）
# 如果我改了模型（比如加一个字段），不会自动更新表

# SQLite 文件会自动创建吗！是的，只要调用 `Base.metadata.create_all(bind=engine)`，且 `data/` 目录存在。
os.makedirs("data", exist_ok=True)  # 确保 data/ 目录存在
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="图书馆管理系统",
    debug=settings.APP_ENV == "development",
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
        {"name": "借阅管理", "description": "借书、还书操作"}
    ]
)

# 注册异常处理函数
register_exception_handlers(app)
# 注册中间件, 统一管理数据库事务
app.add_middleware(DBSessionMiddleware)


app.include_router(books.router, prefix="/books", tags=["图书管理"])

app.include_router(users.router, prefix="/users", tags=["用户管理"])

app.include_router(borrows.router, prefix="/borrows", tags=["借阅管理"])

app.include_router(auth.router, prefix="/auth", tags=["获取当前token的用户信息"])
# 启动项目
# uvicorn main:app --reload
# 修改端口
# uvicorn main:app --reload --port=8001
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)