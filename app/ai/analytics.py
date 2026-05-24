from collections import Counter
from datetime import datetime

from sqlalchemy import func

from ..models import Book, IssueRecord, User


class AdminAnalyticsAgent:
    def insights(self) -> dict:
        return {
            "most_borrowed_books": self.most_borrowed_books(),
            "inactive_users": self.inactive_users(),
            "peak_borrowing_times": self.peak_borrowing_times(),
            "low_stock_alerts": self.low_stock_alerts(),
            "trending_genres": self.trending_genres(),
        }

    def most_borrowed_books(self, limit: int = 5) -> list[dict]:
        data = (
            Book.query.with_entities(Book.title, func.count(IssueRecord.id).label("count"))
            .join(IssueRecord, Book.id == IssueRecord.book_id)
            .group_by(Book.id)
            .order_by(func.count(IssueRecord.id).desc())
            .limit(limit)
            .all()
        )
        return [{"title": row.title, "borrow_count": int(row.count)} for row in data]

    def inactive_users(self, days: int = 30, limit: int = 10) -> list[dict]:
        threshold = datetime.utcnow().timestamp() - (days * 86400)
        users = User.query.order_by(User.created_at.asc()).all()
        output = []
        for user in users:
            latest_issue = (
                IssueRecord.query.filter_by(user_id=user.id)
                .order_by(IssueRecord.issued_at.desc())
                .first()
            )
            if not latest_issue:
                output.append({"username": user.username, "reason": "No borrowing history"})
            elif latest_issue.issued_at.timestamp() < threshold:
                output.append({"username": user.username, "reason": f"No borrowing in {days} days"})
            if len(output) >= limit:
                break
        return output

    def peak_borrowing_times(self) -> list[dict]:
        records = IssueRecord.query.all()
        if not records:
            return []
        hour_counter = Counter(record.issued_at.hour for record in records if record.issued_at)
        return [
            {"hour": hour, "borrows": count}
            for hour, count in sorted(hour_counter.items(), key=lambda x: x[1], reverse=True)
        ][:5]

    def low_stock_alerts(self, threshold: int = 1) -> list[dict]:
        books = Book.query.filter(Book.available_copies <= threshold).order_by(Book.available_copies.asc()).all()
        return [
            {
                "title": b.title,
                "available_copies": b.available_copies,
                "total_copies": b.total_copies,
            }
            for b in books
        ]

    def trending_genres(self, limit: int = 5) -> list[dict]:
        rows = (
            Book.query.with_entities(Book.category, func.count(IssueRecord.id).label("count"))
            .join(IssueRecord, Book.id == IssueRecord.book_id)
            .group_by(Book.category)
            .order_by(func.count(IssueRecord.id).desc())
            .limit(limit)
            .all()
        )
        return [{"category": row.category, "borrow_count": int(row.count)} for row in rows]
