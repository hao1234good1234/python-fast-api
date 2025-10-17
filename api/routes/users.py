from fastapi import APIRouter, Depends, HTTPException, status
from core.models import User
from core.services import LibraryService
from api.schemas import UserRegisterSchema,UserResponse, to_user_response
from core.dtos import UserCreateDto
from api.dependencies import get_library_service
from core.security import get_password_hash
import uuid
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from core.security import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token
router = APIRouter()
import logging
logger = logging.getLogger(__name__)

@router.post("/register", response_model=UserResponse,summary="注册用户")
def create_user(user_in: UserRegisterSchema, service: LibraryService = Depends(get_library_service)):
    try:
        hashed_pw = get_password_hash(user_in.password)
        dto = UserCreateDto(
            user_id=str(uuid.uuid4()),
            username=user_in.username,
            name=user_in.name,
            hashed_password=hashed_pw,
            is_active=True
        )
        added_user = service.add_user(dto)
        return to_user_response(added_user)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    

# ✅ 使用 `OAuth2PasswordRequestForm` 是 FastAPI 推荐做法，Swagger UI 会自动显示登录框！
@router.post("/token", summary="登录 - 获取 Token")
def login_for_access_token(
    from_data: OAuth2PasswordRequestForm = Depends(),
    service: LibraryService = Depends(get_library_service)
):
    user = service.authenticate_user(from_data.username, from_data.password)
    if not user:
        logger.warning(f"用户 {from_data.username} 登录失败，用户名或密码错误")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无法验证凭据", headers={"WWW-Authenticate": "Bearer"})
    if not user.is_active:
        logger.warning(f"用户 {from_data.username} 登录失败，用户未激活")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户未激活", headers={"WWW-Authenticate": "Bearer"})
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires) # 通常用 username 或 user_id 作为 subject
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/{username}", response_model=UserResponse, summary="根据用户名获取用户")
def get_user(username: str, service: LibraryService = Depends(get_library_service)):
    user = service.get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return to_user_response(user)

@router.get("/", response_model=list[UserResponse], summary="获取所有用户")
def list_users(service: LibraryService = Depends(get_library_service)):
    return [to_user_response(user) for user in service.get_all_users()]


