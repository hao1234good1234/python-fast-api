from pydantic import BaseModel, Field
from core.models import Book
# `BaseModel` 是 Pydantic 的核心类，它会：
# - 自动解析 JSON
# - 校验字段是否存在、类型是否正确
# - 提供类型提示和文档


# 给 `BookCreate` 添加字段说明和示例：
# ...（必填）是必填的字段
class BookCreate(BaseModel):
    isbn: str = Field(..., description="国际标准书号，必须唯一", example="999-0134685994")
    title: str = Field(..., description="图书名称", example="Python编程从入门到精通")
    author: str = Field(..., description="图书作者", example="鲁迅")
    # isbn: str
    # title: str
    # author: str

# 在你当前的项目中，只需要一个 BookResponse 就够了！
# 不需要 BookSummary 或 BookDetail，除非你有明确需求。
class BookResponse(BaseModel):
    isbn: str = Field(..., description="国际标准书号", example="999-0134685994")
    title: str = Field(..., description="图书名称", example="Python编程从入门到精通")
    author: str = Field(..., description="图书作者", example="鲁迅")
    is_borrowed: bool = Field(..., description="是否借阅", example=False)
    borrowed_by: str | None = Field(default=None, description="借阅人（未借出时为 null）", example="u1") 
    class Config:
        # 如果你未来用 ORM，可以加 orm_mode = True
        # 但现在不需要
        pass

def to_book_response(book: Book) -> BookResponse:
    return BookResponse(
        isbn=book.isbn,
        title=book.title,
        author=book.author,
        is_borrowed=book.is_borrowed,
        borrowed_by=book.borrowed_by,
    )
# ✅ 所有地方都需要 borrowed_by 字段！
# 💡 如果未来某天你说：“列表页我不想显示谁借的，只显示是否被借”，那时再加 BookSummary。
# 列表页要精简（不返回借阅人），详情页要完整	✅ 需要两个模型
class BookSummary(BaseModel):
    isbn: str = Field(..., description="国际标准书号", example="999-0134685994")
    title: str = Field(..., description="图书名称", example="Python编程从入门到精通")
    author: str = Field(..., description="图书作者", example="鲁迅")
    is_borrowed: bool = Field(..., description="是否借阅", example=False)
class BookDetail(BookSummary): # 继承复用
    borrowed_by: str | None = Field(default=None, description="借阅人（未借出时为 null）", example="u1")


# 定义安全的响应模型： @dataclassUser的password_hash: str属性比较敏感！不能返回给前端
class UserPublic(BaseModel):
    user_id: str
    name: str
    # 注意：没有 password_hash！