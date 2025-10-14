from fastapi import APIRouter, Depends, HTTPException
from core.models import User
from core.services import LibraryService
from api.schemas import UserCreate, UserResponse, to_user_response
from api.dependencies import get_library_service

router = APIRouter()

@router.post("/", response_model=UserResponse,summary="创建用户")
def create_user(user: UserCreate, service: LibraryService = Depends(get_library_service)):
    existing = service.get_user_by_id(user.user_id)
    if existing:
        raise HTTPException(status_code=400, detail="用户已存在")
    added_user = service.add_user(User(user_id=user.user_id, name=user.name))
    return to_user_response(added_user)

@router.get("/{user_id}", response_model=UserResponse, summary="根据ID获取用户")
def get_user(user_id: str, service: LibraryService = Depends(get_library_service)):
    user = service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return to_user_response(user)

@router.get("/", response_model=list[UserResponse], summary="获取所有用户")
def list_users(service: LibraryService = Depends(get_library_service)):
    return [to_user_response(user) for user in service.get_all_users()]


