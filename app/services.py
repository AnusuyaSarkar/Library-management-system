from collections import Counter
from datetime import datetime, timedelta

from sqlalchemy import desc, func

from . import db
from .models import Book, IssueRecord, Notification, Reservation

DEFAULT_LOAN_DAYS = 14
DAILY_FINE = 2.0


def calculate_fine(due_date, returned_at=None):
    returned_at = returned_at or datetime.utcnow()
    if returned_at <= due_date:
        return 0.0
    days_late = (returned_at.date() - due_date.date()).days
    return float(days_late * DAILY_FINE)


def issue_book(user_id, book_id, days=DEFAULT_LOAN_DAYS):
    book = db.session.get(Book, book_id)
    if not book:
        return False, "Book not found."
    if book.available_copies <= 0:
        return False, "Book unavailable. Please reserve it."

    record = IssueRecord(
        user_id=user_id,
        book_id=book_id,
        due_date=datetime.utcnow() + timedelta(days=days),
    )
    book.available_copies -= 1
    db.session.add(record)
    db.session.commit()
    return True, "Book issued successfully."


def return_book(issue_id):
    record = db.session.get(IssueRecord, issue_id)
    if not record or record.returned_at:
        return False, "Invalid issue record."

    record.returned_at = datetime.utcnow()
    record.fine_amount = calculate_fine(record.due_date, record.returned_at)
    record.book.available_copies += 1
    db.session.commit()
    process_reservations(record.book_id)
    return True, f"Book returned. Fine: Rs. {record.fine_amount:.2f}"


def reserve_book(user_id, book_id):
    existing = Reservation.query.filter_by(
        user_id=user_id, book_id=book_id, status="active"
    ).first()
    if existing:
        return False, "You already have an active reservation."

    reservation = Reservation(user_id=user_id, book_id=book_id, status="active")
    db.session.add(reservation)
    db.session.commit()
    return True, "Reservation placed successfully."


def process_reservations(book_id):
    book = db.session.get(Book, book_id)
    if not book or book.available_copies <= 0:
        return

    next_reservation = (
        Reservation.query.filter_by(book_id=book_id, status="active")
        .order_by(Reservation.created_at.asc())
        .first()
    )
    if next_reservation:
        message = (
            f"Reserved book '{book.title}' is now available for you. "
            "Please issue it soon."
        )
        db.session.add(Notification(user_id=next_reservation.user_id, message=message))
        next_reservation.status = "notified"
        db.session.commit()


def generate_due_notifications():
    now = datetime.utcnow()
    due_soon = now + timedelta(days=2)
    active_issues = IssueRecord.query.filter(IssueRecord.returned_at.is_(None)).all()
    created = 0

    for issue in active_issues:
        if issue.due_date < now:
            message = f"Overdue: '{issue.book.title}' was due on {issue.due_date.date()}."
        elif now <= issue.due_date <= due_soon:
            message = f"Reminder: '{issue.book.title}' is due on {issue.due_date.date()}."
        else:
            continue

        exists = Notification.query.filter_by(user_id=issue.user_id, message=message).first()
        if not exists:
            db.session.add(Notification(user_id=issue.user_id, message=message))
            created += 1

    if created > 0:
        db.session.commit()
    return created


def recommendation_for_user(user_id, limit=5):
    history = (
        db.session.query(Book.category)
        .join(IssueRecord, Book.id == IssueRecord.book_id)
        .filter(IssueRecord.user_id == user_id)
        .all()
    )
    if not history:
        return Book.query.order_by(Book.created_at.desc()).limit(limit).all()

    category_counts = Counter([c[0] for c in history])
    top_category = category_counts.most_common(1)[0][0]
    return (
        Book.query.filter_by(category=top_category)
        .order_by(Book.available_copies.desc(), Book.title.asc())
        .limit(limit)
        .all()
    )


def analytics_summary():
    most_borrowed = (
        db.session.query(Book.title, func.count(IssueRecord.id).label("borrow_count"))
        .join(IssueRecord, Book.id == IssueRecord.book_id)
        .group_by(Book.id)
        .order_by(desc("borrow_count"))
        .limit(5)
        .all()
    )

    monthly_usage = (
        db.session.query(
            func.strftime("%Y-%m", IssueRecord.issued_at).label("month"),
            func.count(IssueRecord.id).label("count"),
        )
        .group_by("month")
        .order_by("month")
        .all()
    )

    return {"most_borrowed": most_borrowed, "monthly_usage": monthly_usage}
