from datetime import datetime, timedelta

from app import create_app, db
from app.models import Book, IssueRecord, User
from app.services import calculate_fine, issue_book, reserve_book, return_book


def setup_app():
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SECRET_KEY": "test-key",
        }
    )
    with app.app_context():
        db.drop_all()
        db.create_all()
    return app


def test_fine_calculation():
    due = datetime.utcnow() - timedelta(days=3)
    assert calculate_fine(due) == 6.0


def test_issue_and_return_flow():
    app = setup_app()
    with app.app_context():
        user = User(username="u1", email="u1@example.com", role="user")
        user.set_password("123456")
        book = Book(
            title="Test Book",
            author="Author",
            category="Tech",
            isbn="ISBN001",
            total_copies=1,
            available_copies=1,
            barcode="BAR-ISBN001",
            qr_code="QR-ISBN001",
        )
        db.session.add_all([user, book])
        db.session.commit()

        success, _ = issue_book(user.id, book.id)
        assert success is True
        assert book.available_copies == 0

        issue = IssueRecord.query.first()
        issue.due_date = datetime.utcnow() - timedelta(days=2)
        db.session.commit()

        success, message = return_book(issue.id)
        assert success is True
        assert "Fine" in message
        assert book.available_copies == 1


def test_reservation_when_unavailable():
    app = setup_app()
    with app.app_context():
        user = User(username="u2", email="u2@example.com", role="user")
        user.set_password("123456")
        book = Book(
            title="Reserved Book",
            author="Author",
            category="Fiction",
            isbn="ISBN002",
            total_copies=1,
            available_copies=0,
            barcode="BAR-ISBN002",
            qr_code="QR-ISBN002",
        )
        db.session.add_all([user, book])
        db.session.commit()

        success, _ = reserve_book(user.id, book.id)
        assert success is True
