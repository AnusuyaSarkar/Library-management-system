from collections import Counter
from typing import Iterable

from sqlalchemy import or_

from ..models import Book, IssueRecord, Review


class RecommendationEngine:
    def recommend_for_user(self, user_id: int, limit: int = 5, keyword: str = "") -> list[Book]:
        borrowed_books = (
            Book.query.join(IssueRecord, Book.id == IssueRecord.book_id)
            .filter(IssueRecord.user_id == user_id)
            .all()
        )
        reviewed_books = (
            Book.query.join(Review, Book.id == Review.book_id).filter(Review.user_id == user_id).all()
        )

        preferred_categories = self._top_values([b.category for b in borrowed_books + reviewed_books], 2)
        preferred_authors = self._top_values([b.author for b in borrowed_books + reviewed_books], 2)
        seen_ids = {b.id for b in borrowed_books + reviewed_books}

        query = Book.query
        if keyword:
            keyword_filter = f"%{keyword}%"
            query = query.filter(
                or_(
                    Book.title.ilike(keyword_filter),
                    Book.author.ilike(keyword_filter),
                    Book.category.ilike(keyword_filter),
                )
            )

        if preferred_categories or preferred_authors:
            filters = []
            for category in preferred_categories:
                filters.append(Book.category == category)
            for author in preferred_authors:
                filters.append(Book.author == author)
            query = query.filter(or_(*filters))

        ranked = query.order_by(Book.available_copies.desc(), Book.created_at.desc()).all()
        ranked = [book for book in ranked if book.id not in seen_ids]

        if len(ranked) < limit:
            trending = self._trending_books(limit=limit * 2)
            existing_ids = {book.id for book in ranked}
            for book in trending:
                if book.id in existing_ids or book.id in seen_ids:
                    continue
                ranked.append(book)
                existing_ids.add(book.id)
                if len(ranked) >= limit:
                    break

        return ranked[:limit]

    def _trending_books(self, limit: int = 10) -> list[Book]:
        counts = (
            IssueRecord.query.with_entities(IssueRecord.book_id)
            .filter(IssueRecord.book_id.is_not(None))
            .all()
        )
        if not counts:
            return Book.query.order_by(Book.created_at.desc()).limit(limit).all()

        order = [book_id for book_id, _ in Counter([row.book_id for row in counts]).most_common(limit * 2)]
        books = Book.query.filter(Book.id.in_(order)).all()
        by_id = {b.id: b for b in books}
        sorted_books = [by_id[book_id] for book_id in order if book_id in by_id]
        return sorted_books[:limit]

    def _top_values(self, values: Iterable[str], top_n: int) -> list[str]:
        clean = [value for value in values if value]
        return [value for value, _ in Counter(clean).most_common(top_n)]
