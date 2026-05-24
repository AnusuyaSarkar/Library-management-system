from datetime import datetime, timedelta

from app import create_app, db
from app.ai import LibraryAIAgent
from app.models import Book, IssueRecord, User


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


def seed_data():
    user = User(username="reader", email="reader@example.com", role="user")
    user.set_password("123456")
    admin = User(username="admin2", email="admin2@example.com", role="admin")
    admin.set_password("123456")
    books = [
        Book(
            title="Mystery Starter",
            author="A. Writer",
            category="Mystery",
            isbn="AI001",
            total_copies=2,
            available_copies=2,
            barcode="BAR-AI001",
            qr_code="QR-AI001",
        ),
        Book(
            title="Detective Cases",
            author="A. Writer",
            category="Thriller",
            isbn="AI002",
            total_copies=2,
            available_copies=2,
            barcode="BAR-AI002",
            qr_code="QR-AI002",
        ),
        Book(
            title="Java Basics 101",
            author="B. Teacher",
            category="Programming",
            isbn="AI003",
            total_copies=3,
            available_copies=3,
            barcode="BAR-AI003",
            qr_code="QR-AI003",
        ),
    ]
    db.session.add_all([user, admin] + books)
    db.session.commit()

    issue = IssueRecord(
        user_id=user.id,
        book_id=books[0].id,
        due_date=datetime.utcnow() - timedelta(days=1),
    )
    books[0].available_copies -= 1
    db.session.add(issue)
    db.session.commit()
    return user, admin, books, issue


def test_chatbot_due_date_and_fine():
    app = setup_app()
    with app.app_context():
        user, _, _, _ = seed_data()
        agent = LibraryAIAgent()

        due = agent.chat(user.id, "What is my due date?")
        assert "due dates" in due["reply"].lower()
        assert len(due["data"]) == 1

        fine = agent.chat(user.id, "How much fine do I need to pay?")
        assert "payable fine" in fine["reply"].lower()


def test_nl_search_and_recommendations():
    app = setup_app()
    with app.app_context():
        user, _, _, _ = seed_data()
        agent = LibraryAIAgent()

        results = agent.nl_search("Show beginner books for Java")
        assert any("Java" in item["title"] for item in results)

        recs = agent.recommend(user.id, keyword="mystery", limit=5)
        assert isinstance(recs, list)


def test_chatbot_availability_query():
    app = setup_app()
    with app.app_context():
        user, _, books, _ = seed_data()
        agent = LibraryAIAgent()

        result = agent.chat(user.id, f"Do you have {books[2].title}?")
        assert "availability" in result["reply"].lower()
        assert len(result["data"]) >= 1
        assert result["data"][0]["title"] == books[2].title
        assert "is_available" in result["data"][0]


def test_admin_analytics_and_summary():
    app = setup_app()
    with app.app_context():
        _, _, books, _ = seed_data()
        agent = LibraryAIAgent()

        insights = agent.analytics()
        assert "most_borrowed_books" in insights
        assert "trending_genres" in insights

        summary = agent.summarize_book(books[2].id)
        assert summary["difficulty_level"] in {"Beginner", "Intermediate", "Advanced"}
