import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class QueryIntent:
    intent: str
    title: Optional[str] = None
    author: Optional[str] = None
    category: Optional[str] = None
    keyword: Optional[str] = None


class NLPEngine:
    """
    Lightweight rule-based NLP parser for beginner-friendly projects.
    """

    def parse(self, query: str) -> QueryIntent:
        text = (query or "").strip()
        lower = text.lower()

        if not text:
            return QueryIntent(intent="unknown")

        author_match = re.search(r"by\s+([a-zA-Z0-9 .'-]+)", text, flags=re.IGNORECASE)
        author = author_match.group(1).strip() if author_match else None

        availability_phrases = (
            "available",
            "do you have",
            "in stock",
            "is there",
            "can i get",
            "can i borrow",
        )
        if any(phrase in lower for phrase in availability_phrases):
            return QueryIntent(intent="availability", title=self._extract_title(text))

        if "due date" in lower or "when is" in lower and "due" in lower:
            return QueryIntent(intent="due_date")

        if "fine" in lower or "pay" in lower and "fine" in lower:
            return QueryIntent(intent="fine")

        if "recommend" in lower or "suggest" in lower:
            keyword = self._extract_topic(text)
            return QueryIntent(intent="recommend", keyword=keyword)

        if "show" in lower and author:
            return QueryIntent(intent="search_author", author=author)

        if "beginner" in lower:
            topic = self._extract_topic(text)
            return QueryIntent(intent="search_beginner", keyword=topic)

        if "related to" in lower:
            topic = self._extract_after_phrase(text, "related to")
            return QueryIntent(intent="search_topic", keyword=topic)

        if "books" in lower and author:
            return QueryIntent(intent="search_author", author=author)

        topic = self._extract_topic(text)
        return QueryIntent(intent="search_topic", keyword=topic)

    def _extract_title(self, text: str) -> Optional[str]:
        quoted = re.search(r"'([^']+)'|\"([^\"]+)\"", text)
        if quoted:
            return quoted.group(1) or quoted.group(2)
        after_phrases = (
            "do you have",
            "is",
            "for",
            "about",
            "available",
            "book",
            "novel",
            "in stock",
            "can i get",
            "can i borrow",
        )
        clean = text
        for phrase in after_phrases:
            clean = re.sub(rf"\b{re.escape(phrase)}\b", " ", clean, flags=re.IGNORECASE)
        clean = re.sub(r"\?", " ", clean)
        clean = re.sub(r"\s+", " ", clean).strip(" .")
        return clean or self._extract_topic(text)

    def _extract_topic(self, text: str) -> Optional[str]:
        clean = re.sub(
            r"\b(show|find|books?|for|about|related|to|suggest|recommend|is|this|available|novels?)\b",
            " ",
            text,
            flags=re.IGNORECASE,
        )
        topic = re.sub(r"\s+", " ", clean).strip(" ?.")
        return topic if topic else None

    def _extract_after_phrase(self, text: str, phrase: str) -> Optional[str]:
        match = re.search(rf"{re.escape(phrase)}\s+(.+)$", text, flags=re.IGNORECASE)
        if not match:
            return None
        return match.group(1).strip(" ?.")
