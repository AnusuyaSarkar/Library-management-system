from functools import wraps

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from .. import db
from ..models import Book, User

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            flash("Admin access required.", "danger")
            return redirect(url_for("main.dashboard"))
        return func(*args, **kwargs)

    return wrapper


@admin_bp.route("/books")
@login_required
@admin_required
def books():
    query = Book.query
    search = request.args.get("search", "").strip()
    category = request.args.get("category", "").strip()
    sort = request.args.get("sort", "title")

    if search:
        query = query.filter((Book.title.ilike(f"%{search}%")) | (Book.author.ilike(f"%{search}%")))
    if category:
        query = query.filter(Book.category.ilike(f"%{category}%"))

    if sort == "author":
        query = query.order_by(Book.author.asc())
    elif sort == "copies":
        query = query.order_by(Book.available_copies.desc())
    else:
        query = query.order_by(Book.title.asc())

    books_list = query.all()
    return render_template("admin_books.html", books=books_list, search=search, category=category, sort=sort)


@admin_bp.route("/books/add", methods=["POST"])
@login_required
@admin_required
def add_book():
    title = request.form.get("title", "").strip()
    author = request.form.get("author", "").strip()
    category = request.form.get("category", "").strip()
    isbn = request.form.get("isbn", "").strip()
    copies = int(request.form.get("copies", "1"))

    if not all([title, author, category, isbn]) or copies < 1:
        flash("Please provide valid book details.", "danger")
        return redirect(url_for("admin.books"))

    if Book.query.filter_by(isbn=isbn).first():
        flash("ISBN already exists.", "warning")
        return redirect(url_for("admin.books"))

    book = Book(
        title=title,
        author=author,
        category=category,
        isbn=isbn,
        total_copies=copies,
        available_copies=copies,
        barcode=f"BAR-{isbn}",
        qr_code=f"QR-{isbn}",
    )
    db.session.add(book)
    db.session.commit()
    flash("Book added successfully.", "success")
    return redirect(url_for("admin.books"))


@admin_bp.route("/books/<int:book_id>/update", methods=["POST"])
@login_required
@admin_required
def update_book(book_id):
    book = Book.query.get_or_404(book_id)
    title = request.form.get("title", "").strip()
    author = request.form.get("author", "").strip()
    category = request.form.get("category", "").strip()
    copies = int(request.form.get("copies", book.total_copies))

    if not all([title, author, category]) or copies < 1:
        flash("Please provide valid details.", "danger")
        return redirect(url_for("admin.books"))

    issued_count = book.total_copies - book.available_copies
    if copies < issued_count:
        flash("Copies cannot be less than currently issued count.", "danger")
        return redirect(url_for("admin.books"))

    book.title = title
    book.author = author
    book.category = category
    book.total_copies = copies
    book.available_copies = copies - issued_count
    db.session.commit()
    flash("Book updated.", "success")
    return redirect(url_for("admin.books"))


@admin_bp.route("/books/<int:book_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    if book.available_copies != book.total_copies:
        flash("Cannot delete a book with active issued copies.", "warning")
        return redirect(url_for("admin.books"))

    db.session.delete(book)
    db.session.commit()
    flash("Book deleted.", "info")
    return redirect(url_for("admin.books"))


@admin_bp.route("/users")
@login_required
@admin_required
def users():
    users_list = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin_users.html", users=users_list)


@admin_bp.route("/users/add", methods=["POST"])
@login_required
@admin_required
def add_user():
    username = request.form.get("username", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    role = request.form.get("role", "user").strip().lower()

    if role not in {"admin", "manager", "user"}:
        role = "user"

    if not username or not email or len(password) < 6:
        flash("Provide valid user details. Password must be at least 6 chars.", "danger")
        return redirect(url_for("admin.users"))

    exists = User.query.filter((User.username == username) | (User.email == email)).first()
    if exists:
        flash("Username or email already exists.", "warning")
        return redirect(url_for("admin.users"))

    user = User(username=username, email=email, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    flash("User added successfully.", "success")
    return redirect(url_for("admin.users"))


@admin_bp.route("/users/<int:user_id>/update", methods=["POST"])
@login_required
@admin_required
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    username = request.form.get("username", "").strip()
    email = request.form.get("email", "").strip().lower()
    role = request.form.get("role", user.role).strip().lower()
    is_active = request.form.get("is_active") == "on"

    if role not in {"admin", "manager", "user"}:
        role = user.role

    if not username or not email:
        flash("Username and email are required.", "danger")
        return redirect(url_for("admin.users"))

    exists = User.query.filter(
        (User.id != user.id) & ((User.username == username) | (User.email == email))
    ).first()
    if exists:
        flash("Another user already uses that username or email.", "warning")
        return redirect(url_for("admin.users"))

    user.username = username
    user.email = email
    user.role = role
    user.is_active = is_active
    db.session.commit()
    flash("User updated.", "success")
    return redirect(url_for("admin.users"))


@admin_bp.route("/users/<int:user_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        flash("You cannot delete your own account.", "warning")
        return redirect(url_for("admin.users"))

    db.session.delete(user)
    db.session.commit()
    flash("User deleted.", "info")
    return redirect(url_for("admin.users"))
