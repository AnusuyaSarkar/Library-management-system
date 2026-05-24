# Library Management System (Flask + SQLite)

A complete beginner-friendly Library Management System built with **Python, Flask, SQLite, and OOP principles**.

## Features Implemented

### 1) Core Features
- Book management (Add, Update, Delete, View) - Admin
- User management (Register, Login, Logout)
- Issue and return books with due dates
- Fine calculation for late returns

### 2) Enhanced Features
- Advanced search by title/author/category
- Filtering and sorting in catalog and admin books
- Reservation for unavailable books
- Dashboard statistics:
  - Total books
  - Issued books
  - Active users
- Due and overdue notifications

### 3) Advanced Features
- Role-based access (`admin`, `user`)
- Recommendation system (based on user's borrowing category)
- Barcode/QR support (simulated fields)
- Analytics:
  - Most borrowed books
  - Monthly usage trends

### 5) AI Agent Module
- Smart recommendations using history + trending + keyword interest
- AI chatbot assistant for natural language user queries
- Natural language search (`/ai/search`)
- Smart reminders for due and overdue books
- Admin AI insights (`/ai/analytics`)
- AI book summary endpoint (`/ai/summary/<book_id>`)

### 4) UI/UX + Bonus
- Clean responsive interface using Bootstrap
- Form validation + error handling with flash messages
- Dark mode toggle (stored in localStorage)
- Book reviews and rating support

---

## Tech Stack
- **Backend:** Flask, Flask-Login, Flask-SQLAlchemy
- **Database:** SQLite (`library.db`)
- **Frontend:** Jinja2 templates + Bootstrap 5
- **Testing:** pytest

---

## Project Structure

```text
Library Management System/
|-- app/
|   |-- __init__.py
|   |-- models.py
|   |-- services.py
|   |-- routes/
|   |   |-- __init__.py
|   |   |-- auth.py
|   |   |-- main.py
|   |   |-- admin.py
|   |   |-- user.py
|   |-- templates/
|   |-- static/
|-- tests/
|   |-- test_core.py
|-- schema.sql
|-- requirements.txt
|-- run.py
```

---

## Database Schema (Tables)

Defined in `schema.sql` and mapped in `app/models.py`:

1. `user` - account details + role
2. `book` - inventory + barcode/QR fields
3. `issue_record` - issue/return lifecycle + fine
4. `reservation` - waiting list for unavailable books
5. `notification` - due/overdue/reservation messages
6. `review` - user ratings/comments

---

## How the System Works (Step-by-step)

1. **User registers and logs in**
   - By default, all registered users are role `user`
   - A default admin account is auto-created:
     - Username: `admin`
     - Password: `admin123`

2. **Admin manages books**
   - Add/update/delete books
   - Search, filter, and sort inventory
   - Track available/total copies

3. **User explores catalog**
   - Search by title/author/category
   - Filter by category and sort options

4. **Issue/Return workflow**
   - If available copies > 0, user can issue book
   - Due date is auto-set (default 14 days)
   - On return, fine is calculated for late days

5. **Reservation workflow**
   - If no copy is available, user can reserve
   - When a copy is returned, next reservation gets a notification

6. **Notifications + dashboard**
   - Due soon and overdue notifications are generated
   - Dashboard shows stats and personal alerts

7. **Recommendations + analytics**
   - User receives recommendations from favorite borrowed category
   - Admin sees most-borrowed books and monthly issue trends

---

## Run Instructions

### 1) Create virtual environment

```bash
python -m venv .venv
```

### 2) Activate environment

Windows PowerShell:

```bash
.venv\Scripts\Activate.ps1
```

### 3) Install dependencies

```bash
pip install -r requirements.txt
```

### 4) Start application

```bash
python run.py
```

### 5) Open browser

[http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## Sample Test Cases

Use pytest:

```bash
pytest -q
```

Included sample tests in `tests/test_core.py`:

1. **Fine calculation**
   - Input: due date 3 days ago
   - Expected fine: `6.0` (at `Rs. 2/day`)

2. **Issue and return flow**
   - Issue decreases available copies
   - Late return applies fine
   - Return increases available copies

3. **Reservation flow**
   - Unavailable book allows reservation

---

## Notes for Beginners

- Business logic is kept in `app/services.py`
- DB models are in `app/models.py`
- Request handling is separated into route files:
  - `auth.py` - login/register/logout
  - `admin.py` - admin operations
  - `user.py` - user operations
  - `main.py` - dashboard/home
- This keeps code maintainable and close to MVC style.

---

## Future Improvements

- Email/SMS notifications
- PDF report export for admin analytics
- Real barcode/QR generation and scanner integration
- Pagination for large catalog
- Background scheduler for notification jobs
- LLM integration for richer conversational AI

---

## AI Module Documentation

Detailed AI module guide, integration steps, API usage, and examples:

- `AI_MODULE.md`
