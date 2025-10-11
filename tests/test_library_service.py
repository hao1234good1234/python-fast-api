# tests/test_library_service.py
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))  # 添加父目录
from unittest.mock import Mock
from core.models import Book, User
from core.services import LibraryService


class TestLibraryService:
    def test_add_book(self):
        # Arrange
        mock_book_repo = Mock()
        mock_user_repo = Mock()
        service = LibraryService(mock_book_repo, mock_user_repo)

        # Act
        book = service.add_book("123", "Python", "Guido")

        # Assert
        assert book.title == "Python"
        mock_book_repo.save.assert_called_once_with(book)

    def test_borrow_book_success(self):
        # Arrange
        mock_book_repo = Mock()
        mock_user_repo = Mock()
        service = LibraryService(mock_book_repo, mock_user_repo)

        # 模拟仓库返回数据
        available_book = Book("123", "Python", "Guido", is_borrowed=False)
        user = User("u1", "Alice")
        mock_book_repo.get_by_isbn.return_value = available_book
        mock_user_repo.get_by_id.return_value = user

        # Act
        result = service.borrow_book("123", "u1")

        # Assert
        assert result is True
        assert available_book.is_borrowed is True
        assert available_book.borrowed_by == "u1"
        mock_book_repo.save.assert_called_once_with(available_book)

    def test_borrow_book_not_found(self):
        mock_book_repo = Mock()
        mock_user_repo = Mock()
        service = LibraryService(mock_book_repo, mock_user_repo)

        mock_book_repo.get_by_isbn.return_value = None  # 书不存在

        result = service.borrow_book("999", "u1")
        assert result is False

    def test_return_book_success(self):
        mock_book_repo = Mock()
        mock_user_repo = Mock()
        service = LibraryService(mock_book_repo, mock_user_repo)

        borrowed_book = Book(
            "123", "Python", "Guido", is_borrowed=True, borrowed_by="u1"
        )
        mock_book_repo.get_by_isbn.return_value = borrowed_book

        result = service.return_book("123")

        assert result is True
        assert borrowed_book.is_borrowed is False
        assert borrowed_book.borrowed_by is None

    def test_get_user_books(self):
        mock_book_repo = Mock()
        mock_user_repo = Mock()
        service = LibraryService(mock_book_repo, mock_user_repo)

        books = [
            Book("1", "A", "X", is_borrowed=True, borrowed_by="u1"),
            Book("2", "B", "Y", is_borrowed=False),
            Book("3", "C", "Z", is_borrowed=True, borrowed_by="u1"),
        ]
        mock_book_repo.list_all.return_value = books

        result = service.get_user_books("u1")

        assert len(result) == 2
        assert all(b.borrowed_by == "u1" for b in result)
