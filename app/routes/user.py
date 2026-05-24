from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from .. import db
from ..models import Book, IssueRecord, Review
from ..services import issue_book, reserve_book, return_book

user_bp = Blueprint("user", __name__, url_prefix="/user")


@user_bp.route("/catalog")
@login_required
def catalog():
    query = Book.query
    search = request.args.get("search", "").strip()
    category = request.args.get("category", "").strip()
    sort = request.args.get("sort", "title")

    if search:
        query = query.filter(
            (Book.title.ilike(f"%{search}%"))
            | (Book.author.ilike(f"%{search}%"))
            | (Book.category.ilike(f"%{search}%"))
        )
    if category:
        query = query.filter(Book.category.ilike(f"%{category}%"))

    if sort == "newest":
        query = query.order_by(Book.created_at.desc())
    elif sort == "availability":
        query = query.order_by(Book.available_copies.desc())
    else:
        query = query.order_by(Book.title.asc())

    books = query.all()
    return render_template("catalog.html", books=books, search=search, category=category, sort=sort)


@user_bp.route("/issue/<int:book_id>", methods=["POST"])
@login_required
def issue(book_id):
    success, message = issue_book(current_user.id, book_id)
    flash(message, "success" if success else "warning")
    return redirect(url_for("user.catalog"))


@user_bp.route("/reserve/<int:book_id>", methods=["POST"])
@login_required
def reserve(book_id):
    success, message = reserve_book(current_user.id, book_id)
    flash(message, "success" if success else "warning")
    return redirect(url_for("user.catalog"))


@user_bp.route("/my-books")
@login_required
def my_books():
    records = (
        IssueRecord.query.filter_by(user_id=current_user.id)
        .order_by(IssueRecord.issued_at.desc())
        .all()
    )
    return render_template("my_books.html", records=records)


@user_bp.route("/return/<int:issue_id>", methods=["POST"])
@login_required
def return_issued_book(issue_id):
    success, message = return_book(issue_id)
    flash(message, "success" if success else "warning")
    return redirect(url_for("user.my_books"))


@user_bp.route("/review/<int:book_id>", methods=["POST"])
@login_required
def add_review(book_id):
    rating = int(request.form.get("rating", "5"))
    comment = request.form.get("comment", "").strip()
    if rating < 1 or rating > 5:
        flash("Rating must be between 1 and 5.", "danger")
        return redirect(url_for("user.catalog"))

    review = Review(user_id=current_user.id, book_id=book_id, rating=rating, comment=comment)
    db.session.add(review)
    db.session.commit()
    flash("Review added.", "success")
    return redirect(url_for("user.catalog"))
