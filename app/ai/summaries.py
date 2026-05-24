from ..models import Book


class BookSummaryAgent:
    def summarize(self, book: Book) -> dict:
        difficulty = self._infer_difficulty(book)
        target_readers = self._infer_target_readers(book, difficulty)
        overview = (
            f"'{book.title}' by {book.author} is categorized under {book.category}. "
            f"It is suitable for {target_readers} and currently has {book.available_copies} copy/copies available."
        )
        return {
            "title": book.title,
            "author": book.author,
            "topic_overview": overview,
            "difficulty_level": difficulty,
            "target_readers": target_readers,
        }

    def _infer_difficulty(self, book: Book) -> str:
        title = book.title.lower()
        category = book.category.lower()
        beginner_tokens = ["intro", "beginner", "basics", "101", "starter"]
        advanced_tokens = ["advanced", "deep", "architecture", "expert", "professional"]
        if any(token in title or token in category for token in beginner_tokens):
            return "Beginner"
        if any(token in title or token in category for token in advanced_tokens):
            return "Advanced"
        return "Intermediate"

    def _infer_target_readers(self, book: Book, difficulty: str) -> str:
        if difficulty == "Beginner":
            return "students and first-time learners"
        if difficulty == "Advanced":
            return "experienced readers and professionals"
        return "intermediate learners and enthusiasts"
