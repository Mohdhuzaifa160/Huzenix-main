"""
Intent parser for Huzenix.
Smartly distinguishes between commands and casual conversation.
"""

from enum import Enum
from typing import Tuple


class Intent(Enum):
    TIME = "time"
    DATE = "date"
    WEATHER = "weather"
    NOTES = "notes"
    REMINDERS = "reminders"
    CALCULATOR = "calculator"
    FILES = "files"
    HELP = "help"
    EXIT = "exit"
    CONVERSATION = "conversation"


class IntentParser:
    """
    Rule-based intent parser with confidence scoring.
    """

    INTENT_KEYWORDS = {
        Intent.TIME: ["time", "samay"],
        Intent.DATE: ["date", "aaj", "today"],
        Intent.WEATHER: ["weather", "mausam", "temperature", "rain"],
        Intent.NOTES: ["note", "notes", "likh", "padho"],
        Intent.REMINDERS: ["reminder", "remind", "yaad"],
        Intent.FILES: ["file", "folder", "directory", "delete file"],
        Intent.HELP: ["help", "commands", "what can you do"],
        Intent.EXIT: ["exit", "quit", "bye", "goodbye"],
        Intent.CALCULATOR: ["calculate", "plus", "minus", "into", "divide", "+", "-", "*", "/"],
    }

    @staticmethod
    def parse(query: str) -> Tuple[Intent, float]:
        """
        Returns (Intent, confidence)
        """
        if not query or not query.strip():
            return Intent.CONVERSATION, 0.0

        text = query.lower()

        best_intent = Intent.CONVERSATION
        best_score = 0.0

        for intent, keywords in IntentParser.INTENT_KEYWORDS.items():
            score = IntentParser._score(text, keywords)
            if score > best_score:
                best_score = score
                best_intent = intent

        # 🔥 Decision rule
        if best_score < 0.35:
            return Intent.CONVERSATION, best_score

        return best_intent, best_score

    @staticmethod
    def _score(text: str, keywords: list) -> float:
        hits = sum(1 for kw in keywords if kw in text)
        if hits == 0:
            return 0.0
        # stronger weighting
        return min(1.0, hits * 0.5)

    @staticmethod
    def requires_security(intent: Intent) -> bool:
        return intent in {Intent.FILES}
