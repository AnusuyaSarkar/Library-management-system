from ..models import Book
from .analytics import AdminAnalyticsAgent
from .chatbot import LibraryChatbotAssistant
from .recommender import RecommendationEngine
from .reminders import ReminderAgent
from .search import NaturalLanguageSearchAgent
from .summaries import BookSummaryAgent


class LibraryAIAgent:
    """
    Facade over all AI sub-agents.
    """

    def __init__(self):
        self.recommender = RecommendationEngine()
        self.search_agent = NaturalLanguageSearchAgent()
        self.reminder_agent = ReminderAgent()
        self.analytics_agent = AdminAnalyticsAgent()
        self.summary_agent = BookSummaryAgent()
        self.chatbot = LibraryChatbotAssistant(self.search_agent, self.recommender)

    def recommend(self, user_id: int, keyword: str = "", limit: int = 5):
        books = self.recommender.recommend_for_user(user_id=user_id, keyword=keyword, limit=limit)
        return [{"id": b.id, "title": b.title, "author": b.author, "category": b.category} for b in books]

    def chat(self, user_id: int, query: str):
        return self.chatbot.answer(user_id=user_id, query=query)

    def nl_search(self, query: str, limit: int = 10):
        books = self.search_agent.search(query=query, limit=limit)
        return [
            {
                "id": b.id,
                "title": b.title,
                "author": b.author,
                "category": b.category,
                "available_copies": b.available_copies,
            }
            for b in books
        ]

    def reminders(self, user_id: int):
        return self.reminder_agent.generate_user_reminders(user_id)

    def persist_reminders(self, user_id: int):
        return self.reminder_agent.persist_reminders(user_id)

    def analytics(self):
        return self.analytics_agent.insights()

    def summarize_book(self, book_id: int):
        book = Book.query.get(book_id)
        if not book:
            return None
        return self.summary_agent.summarize(book)
