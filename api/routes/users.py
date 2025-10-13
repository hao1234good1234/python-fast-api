from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.models import User
from infrastructure.user_repository import SqlAlchemyUserRepository
from infrastructure.database import get_db_session

router = APIRouter()

@router.post("/", response_model=User,summary="创建用户")
def create_user(user: User, session: Session = Depends(get_db_session)):
    repo = SqlAlchemyUserRepository(session)
    existing = repo.get_by_id(user.user_id)
    if existing:
        raise HTTPException(status_code=400, detail="用户已存在")
    return repo.create(user)

@router.get("/{user_id}", response_model=User, summary="根据ID获取用户")
def get_user(user_id: str, session: Session = Depends(get_db_session)):
    repo = SqlAlchemyUserRepository(session)
    user = repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user

@router.get("/", response_model=list[User], summary="获取所有用户")
def list_users(session: Session = Depends(get_db_session)):
    repo = SqlAlchemyUserRepository(session)
    return repo.get_all()


