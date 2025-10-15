# Pydantic 模型
from pydantic import BaseModel, Field
from core.models import Book, User
# `BaseModel` 是 Pydantic 的核心类，它会：
# - 自动解析 JSON
# - 校验字段是否存在、类型是否正确
# - 提供类型提示和文档


# 给 `BookCreate` 添加字段说明和示例：
# ...（必填）是必填的字段
class BookCreate(BaseModel):
    isbn: str = Field(..., description="国际标准书号，必须唯一", example="999-0134685994")
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
    borrowed_by: str | None = Field(default=None, description="借阅人（未借出时为 null）", example="u1") 

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
class BookDetail(BookSummary): # 继承复用
    borrowed_by: str | None = Field(default=None, description="借阅人（未借出时为 null）", example="u1")




# 定义安全的请求模型
class UserCreateSchema(BaseModel):
    user_id: str = Field(..., description="用户 ID", example="u001")
    name: str = Field(..., description="用户姓名", example="张三") # `name` 是用于展示的昵称或真实姓名（可重复、可修改）
    username: str = Field(..., description="用户登录名", example="zhangsan")  # **`username` 是用于登录的身份凭证（唯一、不可变）
    password: str # 明文用于传输,不要保存在数据库中！只用于后端验证！不返回给前端！

# 定义安全的响应模型： @dataclassUser的password_hash: str属性比较敏感！不能返回给前端
class UserResponse(BaseModel):
    user_id: str = Field(..., description="用户 ID", example="u001")
    name: str = Field(..., description="用户姓名", example="张三")
    username: str = Field(..., description="用户登录名", example="zhangsan")
    # 不返回 hashed_password！
    # ⚠️ 注意：**永远不要把 `password` 字段存入数据库或返回给前端！**
    # ✅ 不要包含 hashed_password —— domain 层和 API 层都不该接触密码哈希！



def to_user_response(user: User) -> UserResponse:
    return UserResponse(user_id=user.user_id, name=user.name, username=user.username)


class BorrowRequest(BaseModel):
    user_id: str = Field(..., description="用户 ID", example="u1")
    isbn: str = Field(..., description="国际标准书号", example="999-0134685994")

class CommonResponse(BaseModel):
    message: str
