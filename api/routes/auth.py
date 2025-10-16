from fastapi import APIRouter, Depends
from core.models import User
from api.dependencies import get_current_user

router = APIRouter()
# 创建受保护的路由
@router.get("/users/me", summary="获取当前token的用户信息")
def read_users_me(current_user: User = Depends(get_current_user)):
    return {
        "user_id": current_user.user_id,
        "username": current_user.username,
        "name": current_user.name,
        "is_active": current_user.is_active
        # 注意不要返回 hashed_password
    }