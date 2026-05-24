from sqlalchemy import or_

from ..models import Book
from .nlp import NLPEngine


class NaturalLanguageSearchAgent:
    def __init__(self):
        self.nlp = NLPEngine()

    def search(self, query: str, limit: int = 10) -> list[Book]:
        intent = self.nlp.parse(query)
        q = Book.query

        if intent.author:
            q = q.filter(Book.author.ilike(f"%{intent.author}%"))
        elif intent.keyword:
            tokens = [token for token in intent.keyword.split() if len(token) >= 3]
            filters = []
            for token in tokens:
                token_like = f"%{token}%"
                filters.append(Book.title.ilike(token_like))
                filters.append(Book.author.ilike(token_like))
                filters.append(Book.category.ilike(token_like))
            if not filters:
                keyword = f"%{intent.keyword}%"
                filters = [
                    Book.title.ilike(keyword),
                    Book.author.ilike(keyword),
                    Book.category.ilike(keyword),
                ]
            q = q.filter(or_(*filters))

        if intent.intent == "search_beginner":
            q = q.order_by(Book.available_copies.desc(), Book.title.asc())
        else:
            q = q.order_by(Book.created_at.desc())

        return q.limit(limit).all()
