from datetime import datetime

from flask import Blueprint, render_template
from flask_login import current_user, login_required

from ..models import Book, IssueRecord, Notification, User
from ..services import analytics_summary, generate_due_notifications, recommendation_for_user

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    return render_template("home.html")


@main_bp.route("/dashboard")
@login_required
def dashboard():
    generate_due_notifications()

    total_books = Book.query.count()
    issued_books = IssueRecord.query.filter(IssueRecord.returned_at.is_(None)).count()
    active_users = User.query.filter_by(is_active=True).count()

    user_notifications = (
        Notification.query.filter_by(user_id=current_user.id)
        .order_by(Notification.created_at.desc())
        .limit(10)
        .all()
    )
    recommendations = recommendation_for_user(current_user.id)
    analytics = analytics_summary() if current_user.role in {"admin", "manager", "user"} else None
    overdue_count = (
        IssueRecord.query.filter(
            IssueRecord.user_id == current_user.id,
            IssueRecord.returned_at.is_(None),
            IssueRecord.due_date < datetime.utcnow(),
        ).count()
    )

    return render_template(
        "dashboard.html",
        total_books=total_books,
        issued_books=issued_books,
        active_users=active_users,
        notifications=user_notifications,
        recommendations=recommendations,
        analytics=analytics,
        overdue_count=overdue_count,
    )
