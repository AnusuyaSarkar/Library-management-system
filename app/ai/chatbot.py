from datetime import datetime

from ..models import Book, IssueRecord
from ..services import calculate_fine
from .nlp import NLPEngine


class LibraryChatbotAssistant:
    def __init__(self, search_agent, recommendation_engine):
        self.nlp = NLPEngine()
        self.search_agent = search_agent
        self.recommendation_engine = recommendation_engine

    def answer(self, user_id: int, query: str) -> dict:
        intent = self.nlp.parse(query)
        handler = getattr(self, f"_handle_{intent.intent}", self._handle_default)
        return handler(user_id=user_id, intent=intent, query=query)

    def _handle_availability(self, user_id: int, intent, query: str) -> dict:
        if not intent.title:
            return {"reply": "Please share the book title to check availability.", "data": []}
        matches = Book.query.filter(Book.title.ilike(f"%{intent.title}%")).limit(5).all()
        if not matches:
            return {"reply": "No matching book found.", "data": []}
        data = [
            {
                "title": b.title,
                "author": b.author,
                "available_copies": b.available_copies,
                "is_available": b.available_copies > 0,
            }
            for b in matches
        ]
        return {"reply": "Here is the availability status.", "data": data}

    def _handle_recommend(self, user_id: int, intent, query: str) -> dict:
        books = self.recommendation_engine.recommend_for_user(
            user_id=user_id, limit=5, keyword=intent.keyword or ""
        )
        if not books:
            return {"reply": "I could not find recommendations right now.", "data": []}
        return {
            "reply": "Recommended books for you:",
            "data": [{"title": b.title, "author": b.author, "category": b.category} for b in books],
        }

    def _handle_due_date(self, user_id: int, intent, query: str) -> dict:
        active = (
            IssueRecord.query.filter_by(user_id=user_id, returned_at=None)
            .order_by(IssueRecord.due_date.asc())
            .all()
        )
        if not active:
            return {"reply": "You do not have any active issued books.", "data": []}
        return {
            "reply": "Here are your due dates:",
            "data": [{"book": item.book.title, "due_date": item.due_date.date().isoformat()} for item in active],
        }

    def _handle_fine(self, user_id: int, intent, query: str) -> dict:
        now = datetime.utcnow()
        active = IssueRecord.query.filter_by(user_id=user_id, returned_at=None).all()
        total_fine = 0.0
        breakdown = []
        for issue in active:
            fine = calculate_fine(issue.due_date, now)
            if fine > 0:
                total_fine += fine
                breakdown.append({"book": issue.book.title, "fine": fine})
        if total_fine == 0.0:
            return {"reply": "You currently have no overdue fine.", "data": []}
        return {"reply": f"Your current payable fine is Rs. {total_fine:.2f}.", "data": breakdown}

    def _handle_search_author(self, user_id: int, intent, query: str) -> dict:
        books = self.search_agent.search(f"books by {intent.author}", limit=10)
        return {
            "reply": f"Books by {intent.author}:",
            "data": [{"title": b.title, "category": b.category} for b in books],
        }

    def _handle_search_topic(self, user_id: int, intent, query: str) -> dict:
        books = self.search_agent.search(query, limit=10)
        return {
            "reply": "Here are relevant books:",
            "data": [{"title": b.title, "author": b.author, "category": b.category} for b in books],
        }

    def _handle_search_beginner(self, user_id: int, intent, query: str) -> dict:
        books = self.search_agent.search(query, limit=10)
        return {
            "reply": "Beginner-friendly options:",
            "data": [{"title": b.title, "author": b.author, "category": b.category} for b in books],
        }

    def _handle_default(self, user_id: int, intent, query: str) -> dict:
        return {
            "reply": (
                "I can help with availability, recommendations, due dates, fines, and author/topic search."
            ),
            "data": [],
        }
