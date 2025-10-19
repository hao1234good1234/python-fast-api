from sqlalchemy.orm import Session
from .models import UserDB
from core.models import User
from core.interfaces import UserRepository
from core.dtos import UserCreateDto

class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, session: Session):
        self._session = session
    def add(self, user: UserCreateDto) -> User:
        db_user = UserDB(user_id=user.user_id, name=user.name, username=user.username, hashed_password=user.hashed_password, is_active=user.is_active)
        self._session.add(db_user)
        self._session.flush()  # 立即获取生成的 ID，但不 commit
        return self._to_domain(db_user)
    
    def get_by_id(self, user_id: str) -> User | None:
        db_user = self._session.query(UserDB).filter(UserDB.user_id == user_id).first()
        return self._to_domain(db_user) if db_user else None
    
    def get_all(self) -> list[User]:
        db_users = self._session.query(UserDB).all()
        return [self._to_domain(db_user) for db_user in db_users]
    
    def get_by_username(self, username: str) -> User | None:
        db_user = self._session.query(UserDB).filter(UserDB.username == username).first()
        return self._to_domain(db_user) if db_user else None

    def _to_domain(self, db_user: UserDB) -> User:
        return User(user_id=db_user.user_id, name=db_user.name, username=db_user.username, is_active=db_user.is_active, hashed_password=db_user.hashed_password)
    
    # 💡 User 暂时不实现 update/delete（按需添加）