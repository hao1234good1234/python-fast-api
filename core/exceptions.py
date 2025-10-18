from fastapi import status, HTTPException
class UnauthorizedException(HTTPException):
    def __init__(self, detail_msg: str = "无法验证凭据"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail_msg,
            headers={"WWW-Authenticate": "Bearer"}
        )
# 定义业务异常（推荐）
class ResourceNotFound(Exception):
    """借阅记录不存在"""
    pass

class ResourcePermissionDenied(Exception):
    """无权操作他人的借阅记录"""
    pass
