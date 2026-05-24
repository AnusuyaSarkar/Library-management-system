from datetime import datetime, timedelta

from .. import db
from ..models import IssueRecord, Notification
from ..services import DAILY_FINE, calculate_fine


class ReminderAgent:
    def generate_user_reminders(self, user_id: int) -> list[dict]:
        now = datetime.utcnow()
        due_window = now + timedelta(days=2)
        active_issues = IssueRecord.query.filter_by(user_id=user_id, returned_at=None).all()
        reminders = []

        for issue in active_issues:
            if issue.due_date < now:
                days_overdue = (now.date() - issue.due_date.date()).days
                fine = calculate_fine(issue.due_date, now)
                message = (
                    f"Overdue: '{issue.book.title}' is overdue by {days_overdue} days. "
                    f"Current fine: Rs. {fine:.2f}. You can return now to stop fine growth."
                )
                reminders.append(
                    {"type": "overdue", "issue_id": issue.id, "message": message, "fine": fine}
                )
            elif issue.due_date <= due_window:
                days_left = (issue.due_date.date() - now.date()).days
                message = (
                    f"Reminder: '{issue.book.title}' is due in {days_left} day(s). "
                    "Would you like to renew it?"
                )
                reminders.append(
                    {"type": "due_soon", "issue_id": issue.id, "message": message, "fine": 0.0}
                )

        return reminders

    def persist_reminders(self, user_id: int) -> int:
        reminders = self.generate_user_reminders(user_id)
        created = 0
        for item in reminders:
            exists = Notification.query.filter_by(user_id=user_id, message=item["message"]).first()
            if exists:
                continue
            db.session.add(Notification(user_id=user_id, message=item["message"]))
            created += 1
        if created:
            db.session.commit()
        return created

    def renewal_message(self, issue_id: int) -> str:
        issue = IssueRecord.query.get(issue_id)
        if not issue or issue.returned_at:
            return "Renewal unavailable for this issue."
        if issue.due_date < datetime.utcnow():
            extra_per_day = DAILY_FINE
            return (
                "This book is already overdue. Please clear the fine before renewal. "
                f"Fine accumulates at Rs. {extra_per_day:.2f} per day."
            )
        return "Renewal possible. Ask admin to extend your due date."
