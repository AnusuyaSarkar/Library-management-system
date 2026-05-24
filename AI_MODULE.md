# AI Agent Module for Library Management System

This module adds intelligent assistance to the existing Flask + SQLite Library Management System.

## 1) What is included

### AI sub-agents

- `RecommendationEngine` (`app/ai/recommender.py`)
  - Uses borrowing history, preferred categories/authors, keyword interests, and trending books.
- `LibraryChatbotAssistant` (`app/ai/chatbot.py`)
  - Answers natural-language user queries using real-time DB data.
- `NaturalLanguageSearchAgent` (`app/ai/search.py`)
  - Converts natural language into book filters.
- `ReminderAgent` (`app/ai/reminders.py`)
  - Due reminders, overdue alerts, fine-aware messages, and renewal suggestions.
- `AdminAnalyticsAgent` (`app/ai/analytics.py`)
  - Most borrowed books, inactive users, peak borrowing times, low stock, trending genres.
- `BookSummaryAgent` (`app/ai/summaries.py`)
  - Creates short, readable summaries with difficulty and target reader hints.
- `LibraryAIAgent` facade (`app/ai/agent.py`)
  - Single integration point for routes/services.

### API endpoints

Added under `app/routes/ai.py`:

- `GET /ai/recommendations?keyword=&limit=`
- `POST /ai/chat`
- `GET /ai/search?query=&limit=`
- `GET /ai/reminders`
- `POST /ai/reminders/persist`
- `GET /ai/summary/<book_id>`
- `GET /ai/analytics` (admin only)

All endpoints are login-protected.

---

## 2) Integration steps (already applied)

1. Created AI package `app/ai/` with modular classes.
2. Added `ai_bp` blueprint in `app/routes/ai.py`.
3. Registered blueprint in `app/__init__.py`.
4. Reused existing SQLAlchemy models (`Book`, `IssueRecord`, `Review`, `Notification`, `User`) for real-time responses.

No extra external AI/ML dependency is required. This keeps the module beginner-friendly and easy to run offline.

---

## 3) Database connectivity logic

The AI module uses current SQLAlchemy models and Flask app context:

- Real-time availability: queries `Book.available_copies`
- Due dates/fines: queries active `IssueRecord` + `calculate_fine()`
- Recommendations:
  - history from `IssueRecord`
  - preferences from borrowed/reviewed books
  - trending from issue counts
- Analytics:
  - grouped issue counts using SQLAlchemy aggregations
- Reminder persistence: writes to `Notification` table

No schema migration is required because this module uses existing tables.

---

## 4) Example prompts and responses

### Chatbot (`POST /ai/chat`)

Request:

```json
{ "query": "Is this book available Data Structures" }
```

Response:

```json
{
  "ok": true,
  "response": {
    "reply": "Here is the availability status.",
    "data": [
      {
        "title": "Data Structures in Python",
        "author": "John Doe",
        "available_copies": 2,
        "is_available": true
      }
    ]
  }
}
```

Other example queries:

- "Suggest books for Data Structures"
- "What is my due date?"
- "How much fine do I need to pay?"
- "Show books by Robert Martin"
- "Books related to machine learning"

### Natural language search (`GET /ai/search`)

`/ai/search?query=Show beginner books for Java`

### Recommendations (`GET /ai/recommendations`)

`/ai/recommendations?keyword=mystery&limit=5`

### Reminders (`GET /ai/reminders`)

Returns due-soon and overdue messages with fine details.

### Admin analytics (`GET /ai/analytics`)

Returns:
- most borrowed books
- inactive users
- peak borrowing times
- low stock alerts
- trending genres

---

## 5) Step-by-step flow

1. User sends request to any `/ai/...` endpoint.
2. Route validates input and authentication.
3. `LibraryAIAgent` routes the task to relevant sub-agent.
4. Sub-agent reads real-time data through SQLAlchemy models.
5. Rule-based NLP (`NLPEngine`) maps free text to intent.
6. Response is returned as structured JSON for UI/API usage.

---

## 6) How to run

1. Activate virtual environment
2. Install requirements:
   - `pip install -r requirements.txt`
3. Run app:
   - `python run.py`
4. Login and test endpoints with browser/API client.

---

## 7) Suggested UI integration

- Add a simple chat box in dashboard that posts to `POST /ai/chat`.
- Add a "Smart Search" input mapped to `GET /ai/search`.
- Add a recommendation card from `GET /ai/recommendations`.
- Add admin insights panel from `GET /ai/analytics`.

---

## 8) Notes

- This is an intelligent rule-based AI module, not a heavy LLM service.
- Easy to extend with:
  - OpenAI/Gemini APIs
  - vector search
  - scheduled background jobs for reminders
  - email/SMS push notifications
