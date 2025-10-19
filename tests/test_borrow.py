import pytest
from unittest.mock import MagicMock
from datetime import datetime, timezone, timedelta

# 被测对象
from core.services import BorrowService

# 依赖项
from infrastructure.book_repository import SqlAlchemyBookRepository
from infrastructure.borrow_repository import SqlAlchemyBorrowRepository
from infrastructure.models import BookDB

@pytest.fixture
def mock_session():
    """模拟数据库会话"""
    return MagicMock()

@pytest.fixture
def borrow_service(mock_session):
    """测试借阅服务"""
    return BorrowService(
        book_repo=SqlAlchemyBookRepository(mock_session),
        borrow_repo=SqlAlchemyBorrowRepository(mock_session)
    )

# 测试用例
def test_borrow_book_success(borrow_service, mock_session):
    # Arrange
    user_id = "user123"
    isbn = "978-0134685991"

    # 这是数据库中已存在的书（由 repo 查询返回）
    db_book = BookDB(
        isbn=isbn,
        title="Effective Python",
        author="Brett Slatkin",
        is_borrowed=False,      # 初始未借出
        borrowed_by=None
    )

    # 模拟 book_repo.get_by_isbn 返回这本书
    mock_session.query.return_value.filter.return_value.first.return_value = db_book

    # 模拟 borrow_repo.create 返回借阅记录
    from core.models import BorrowRecord
    now = datetime.now(timezone.utc)
    due_date = now + timedelta(days=7)
    mock_borrow_record = MagicMock()
    mock_borrow_record.id = 999
    mock_borrow_record.book_isbn = isbn
    mock_borrow_record.borrower_id = user_id
    mock_borrow_record.borrowed_at = now
    mock_borrow_record.due_date = due_date

    borrow_service.borrow_repo.create = MagicMock(return_value=mock_borrow_record)

    # Act
    result = borrow_service.borrow_book(isbn, user_id)

    # Assert
    # ✅ 1. 数据库中的书被更新（注意：是 db_book，不是你传入的 mock_book）
    assert db_book.is_borrowed is True
    assert db_book.borrowed_by == user_id

    # ✅ 2. 借阅记录被创建
    borrow_service.borrow_repo.create.assert_called_once()
    created_borrow = borrow_service.borrow_repo.create.call_args[0][0]
    assert isinstance(created_borrow, BorrowRecord)
    assert created_borrow.book_isbn == isbn
    assert created_borrow.borrower_id == user_id

    # ✅ 3. 返回 DTO 正确
    assert result.borrow_id == 999
    assert result.book_isbn == isbn
    assert result.borrower_id == user_id
    assert result.borrowed_at == now
    assert result.due_date == due_date

    # ❌ 不要断言 add/merge/commit！
    # 因为：
    # - 书已存在 → 走更新分支，不 add
    # - save() 不 commit（由上层控制事务）

