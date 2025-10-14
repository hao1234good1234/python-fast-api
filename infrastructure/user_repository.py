from sqlalchemy.orm import Session
from database.models import UserDB
from core.models import User
from infrastructure.interfaces import UserRepository

class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, session: Session):
        self._session = session
    def create(self, user: User) -> User:
        db_user = UserDB(user_id=user.user_id, name=user.name)
        self._session.add(db_user)
        self._session.commit()
        self._session.refresh(db_user) # 获取数据库生成的值（如默认值）
        return self._to_domain(db_user)
    
    def get_by_id(self, user_id: str) -> User | None:
        db_user = self._session.query(UserDB).filter(UserDB.user_id == user_id).first()
        return self._to_domain(db_user) if db_user else None
    
    def get_all(self) -> list[User]:
        db_users = self._session.query(UserDB).all()
        return [self._to_domain(db_user) for db_user in db_users]

    def _to_domain(self, db_user: UserDB) -> User:
        return User(user_id=db_user.user_id, name=db_user.name)
    
    # 💡 User 暂时不实现 update/delete（按需添加）