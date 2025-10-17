# `get_library_service` 在多个路由文件中重复定义 改进方案：**统一移到 `api/dependencies.py`**
from sqlalchemy.orm import Session
from infrastructure.database import get_db_session
from infrastructure.user_repository import SqlAlchemyUserRepository
from infrastructure.book_repository import SqlAlchemyBookRepository
from infrastructure.borrow_repository import SqlAlchemyBorrowRepository
from core.services import LibraryService, BorrowService
from fastapi.security import OAuth2PasswordBearer  # 导入 OAuth2PasswordBearer
from core.models import User 
from core.security import decode_access_token
from fastapi import Depends
from core.exceptions import UnauthorizedException
from jose import JWTError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token")

def get_library_service(session: Session = Depends(get_db_session)):
    return LibraryService(
        user_repo=SqlAlchemyUserRepository(session),
        book_repo=SqlAlchemyBookRepository(session)
    )

# ✅ 代码复用 + 单一职责 + 易于扩展（比如以后加 `get_audit_service`）


# 创建get_current_user()依赖
# 💡 问题：`get_current_user` 需要访问 `UserRepository`，但它又不能直接 new 一个。  
# ✅ 解决方案：**通过依赖注入传入 `UserRepository`**

# `OAuth2PasswordBearer` 是 FastAPI 提供的一个 **安全依赖类**，它的作用是：

# - 自动从请求头的 `Authorization` 字段中提取 `Bearer <token>`
# - 如果没有提供 token，**自动返回 401 Unauthorized**
# - 在 Swagger UI 中启用 **"Authorize" 按钮**

# 你初始化它时传入 `tokenUrl="token"`，是为了告诉 Swagger：
# > “用户应该去 `/token` 这个接口登录获取 token”


#  注意：这里我们**没有复用 `LibraryService`**，而是直接用了 `SqlAlchemyUserRepository`。  
# 原因：`get_current_user` 是底层认证逻辑，不应该依赖高层业务服务（避免循环依赖或过度耦合）。


def get_current_user(
        token: str = Depends(oauth2_scheme), # 从请求/users/token 中获取返回的token
        db: Session = Depends(get_db_session)
) -> User:
    """根据 token 获取当前用户"""
    try:
        username = decode_access_token(token)
    except JWTError:
        raise UnauthorizedException("无法验证凭据")
    #1. 解码token获取 username
    # 2.用 repository查询用户
    user_repo = SqlAlchemyUserRepository(db)
    user = user_repo.get_by_username(username) 
    if user is None or not user.is_active:  # ⚠️ 不要说“用户不存在”，统一说“凭据无效”
        #  **安全最佳实践**：永远不要区分“用户名不存在”和“密码错误”，避免被暴力枚举用户名。
        raise UnauthorizedException("无法验证凭据")
    return user


def get_borrow_service(session: Session = Depends(get_db_session)):
    return BorrowService(
        book_repo=SqlAlchemyBookRepository(session),
        borrow_repo=SqlAlchemyBorrowRepository(session)
    )