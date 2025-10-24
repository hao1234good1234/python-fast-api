# Pydantic 模型
from pydantic import BaseModel, Field
from core.models import Book, User
from datetime import datetime
from typing import Any
# `BaseModel` 是 Pydantic 的核心类，它会：
# - 自动解析 JSON
# - 校验字段是否存在、类型是否正确
# - 提供类型提示和文档


# 图书管理
# 给 `BookCreate` 添加字段说明和示例：
# ...（必填）是必填的字段
class BookCreate(BaseModel):
    isbn: str = Field(
        ..., description="国际标准书号，必须唯一", example="999-0134685994"
    )
    title: str = Field(..., description="图书名称", example="呐喊")
    author: str = Field(..., description="图书作者", example="鲁迅")
    # isbn: str
    # title: str
    # author: str


# 在你当前的项目中，只需要一个 BookResponse 就够了！
# 不需要 BookSummary 或 BookDetail，除非你有明确需求。
class BookResponse(BaseModel):
    isbn: str = Field(..., description="国际标准书号", example="999-0134685994")
    title: str = Field(..., description="图书名称", example="呐喊")
    author: str = Field(..., description="图书作者", example="鲁迅")
    is_borrowed: bool = Field(..., description="是否借阅", example=False)
    borrowed_by: str | None = Field(
        default=None, description="借阅人（未借出时为 null）", example="u1"
    )


def to_book_response(book: Book) -> BookResponse:
    return BookResponse(
        isbn=book.isbn,
        title=book.title,
        author=book.author,
        is_borrowed=book.is_borrowed,
        borrowed_by=book.borrowed_by,
    )


# 另一种方式：
# （1）如果未来某天你说：“列表页我不想显示谁借的，只显示是否被借”，那时再加 BookSummary。
# （2）列表页要精简（不返回借阅人），只需要 BookSummary
# （3）详情页要完整，需要两个模型：BookSummary 和 BookDetail
class BookSummary(BaseModel):
    isbn: str = Field(..., description="国际标准书号", example="999-0134685994")
    title: str = Field(..., description="图书名称", example="呐喊")
    author: str = Field(..., description="图书作者", example="鲁迅")
    is_borrowed: bool = Field(..., description="是否借阅", example=False)


class BookDetail(BookSummary):  # 继承复用
    borrowed_by: str | None = Field(
        default=None, description="借阅人（未借出时为 null）", example="u1"
    )


# 用户管理
# 定义安全的请求模型


# 用户注册
class UserRegisterSchema(BaseModel):
    username: str = Field(
        ..., description="用户登录名", example="zhangsan"
    )  # **`username` 是用于登录的身份凭证（唯一、不可变）
    password: str = Field(
        ..., description="用户密码", example="请输入密码"
    )  # 明文用于传输,不要保存在数据库中！只用于后端验证！不返回给前端！
    name: str = Field(
        ..., description="用户姓名", example="张三"
    )  # `name` 是用于展示的昵称或真实姓名（可重复、可修改）
    email: str = Field(..., description="用户邮箱", example="hao1234good1234@163.com")


class UserResponse(BaseModel):
    user_id: str = Field(..., description="用户 ID", example="u001")
    username: str = Field(..., description="用户登录名", example="zhangsan")
    name: str = Field(..., description="用户姓名", example="张三")
    is_active: bool = Field(..., description="是否激活", example=True)
    # 🔒 **注意**：`password` 只在请求中出现，**绝不在响应中返回**！
    # 不返回 hashed_password！
    # ⚠️ 注意：**永远不要把 `password` 字段存入数据库或返回给前端！**
    # ✅ 不要包含 hashed_password —— domain 层和 API 层都不该接触密码哈希！


def to_user_response(user: User) -> UserResponse:
    return UserResponse(
        user_id=user.user_id,
        name=user.name,
        username=user.username,
        is_active=user.is_active,
    )


# 分页相关的响应模型
class BorrowItemResponse(BaseModel):
    borrow_id: int = Field(
        alias="id"
    )  # ← 关键！告诉 Pydantic：borrow_id 来自BorrowRecord对象的 id 字段
    book_isbn: str
    book_title: str
    borrowed_at: datetime
    due_date: datetime
    returned_at: datetime | None
    is_returned: bool
    is_overdue: bool

    class Config:
        from_attributes = True  # 允许从普通对象（非 dict）读取
        populate_by_name = True  # 允许通过字段名（即使用了 alias）赋值


class MyBorrowsResponse(BaseModel):
    items: list[BorrowItemResponse]
    total: int
    page: int
    size: int
    pages: int


# 统一成功的响应模型
# 即使你用了 `response_model=SuccessResponse`，Swagger 默认不会显示示例。你需要显式提供。
# 在 `response_model` 中用 `Config` 设置 schema 示例
class SuccessResponse(BaseModel):
    code: str = "SUCCESS"
    message: str = "操作成功"
    data: Any = None

    class Config:
        json_schema_extra = {
            "example": {
                "code": "SUCCESS",
                "message": "操作成功",
                "data": {"isbn": "999-0134685994"},
            }
        }
# 借阅图书返回响应模型
class BookBorrowResponse(BaseModel):
    borrow_id: int
    book_isbn: str
    borrower_id: str
    borrowed_at: datetime
    due_date: datetime
    task_id: str


# 异步任务返回响应模型
class TaskResponse:
    """统一任务响应格式"""
    def __init__(self, task_id: str, state: str, ready: bool):
        self.task_id = task_id
        self.state = state
        self.ready = ready

    def to_response(self) -> dict:
        base = {
            "task_id": self.task_id,
            "status": self.state,
            "ready": self.ready,
        }

        if self.state == "SUCCESS":
            base["message"] = "任务执行成功"
        elif self.state == "FAILURE":
            base["message"] = "任务执行失败"
        elif self.state == "PENDING":
            base["message"] = "任务等待执行"
        elif self.state == "STARTED":
            base["message"] = "任务正在执行中..."
        elif self.state == "RETRY":
            base["message"] = "任务正在重试"
        elif self.state == "REVOKED":
            base["message"] = "任务已被取消"

        return base
    