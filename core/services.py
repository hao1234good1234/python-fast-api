# 创建借阅服务（Borrow Service）
from sqlalchemy.orm import Session
from infrastructure.book_repository import SqlAlchemyBookRepository
from infrastructure.user_repository import SqlAlchemyUserRepository

class BorrowService:
    def __init__(self, session: Session):
        self.book_repo = SqlAlchemyBookRepository(session)
        self.user_repo = SqlAlchemyUserRepository(session)

    def borrow_book(self, user_id: str, isbn: str) -> dict:
        # 1、检查用户是否存在
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("用户不存在")

        # 2. 检查图书是否存在
        book = self.book_repo.get_by_isbn(isbn)
        if not book:
            raise ValueError("图书不存在")

        # 3. 检查图书是否已经被借出
        if book.is_borrowed:
            raise ValueError("图书已经被借出")
        # 4. 更新图书的借阅状态
        book.is_borrowed = True
        book.borrowed_by = user_id
        updated_book = self.book_repo.update(book)

        return {
            "message": f"用户 {user.name} 借阅了图书 {updated_book.title}"
        }
    
    def return_book(self, isbn: str) -> dict:
        # 1. 检查图书是否存在
        book = self.book_repo.get_by_isbn(isbn)
        if not book:
            raise ValueError("图书不存在")
        # 2. 检查图书是否已经被借出
        if not book.is_borrowed:
            raise ValueError("图书未被借出")
        # 3. 还书：重置状态
        book.is_borrowed = False
        book.borrowed_by = None
        updated_book = self.book_repo.update(book)

        return {
            "message": f"图书 {updated_book.title} 已归还"
        }