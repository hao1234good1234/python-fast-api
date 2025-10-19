from fastapi import status, HTTPException


class UnauthorizedException(HTTPException):
    def __init__(self, detail_msg: str = "无法验证凭据"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail_msg,
            headers={"WWW-Authenticate": "Bearer"},
        )


# 所有业务异常的基类
class BusinessException(Exception):
    """所有业务异常的基类"""

    def __init__(self, code: str, message: str, detail: str | None = None):
        self.code = code
        self.message = message
        self.detail = detail
        super().__init__(message)


# 具体的业务异常
# 借书业务
class BookNotFoundError(BusinessException):
    def __init__(self, isbn: str):
        super().__init__(
            code="BOOK_NOT_FOUND",
            message=f"图书 ISBN{isbn} 不存在",
            detail=f"isbn={isbn}",
        )


class BookNotAvailableError(BusinessException):
    def __init__(self, isbn: str, titile: str):
        super().__init__(
            code="BOOK_NOT_AVAILABLE",
            message=f"图书 《{titile}》 已被借出",
            detail=f"isbn={isbn}",
        )

class BorrowLimitExceededError(BusinessException):
    def __init__(self, user_id: str, limit: int):
        super().__init__(
            code="Borrow_LIMIT_EXCEEDED",
            message=f"用户{user_id}的借阅次数已达上限{limit}本",
            detail=f"user_id={user_id}, limit={limit}",
        )

# 还书业务
class BorrowRecordNotFoundError(BusinessException):
    def __init__(self, borrow_id: str):
        super().__init__(
            code="BORROW_RECORD_NOT_FOUND",
            message="借阅记录不存在",
            detail=f"borrow_id={borrow_id}",
        )

class PermissionError(BusinessException):
    def __init__(self, operator_id: str, user_id: str):
        super().__init__(
            code="PERMISSION_DENIED", 
            message="无权操作他人的记录", 
            detail= f"operator_id={operator_id}, user_id={user_id}")
class BookAlreadyReturnError(BusinessException):
    def __init__(self, borrow_id: str):
        super().__init__(
            code="BOOK_ALREADY_RETURNED",
            message="该图书已归还",
            detail=f"borrow_id={borrow_id}",
        )

# 用户业务
class UsernameExistsError(BusinessException):
    def __init__(self, username: str):
        super().__init__(
            code="USERNAME_EXISTS",
            message=f"用户名 {username} 已存在",
            detail=f"username={username}",
        )

# 图书业务
class BookExistsError(BusinessException):
    def __init__(self, isbn: str):
        super().__init__(
            code="BOOK_EXISTS",
            message=f"图书 ISBN{isbn} 已存在",
            detail=f"isbn={isbn}",
        )

# - 异常自带 **错误码（code）**，前端可做 switch 判断
# - `message` 给用户看，`detail` 给开发者看（日志用）
# - 继承关系清晰，便于全局捕获
