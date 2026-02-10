"""
Conversation engine for Huzenix.
Conversation-first, coding-aware, memory-aware.
"""

from typing import Callable, Dict
from core.intent_parser import Intent, IntentParser
from core.llm_client import ask_llm

CONFIDENCE_THRESHOLD = 0.45
ROLE_USER = "user"
ROLE_ASSISTANT = "assistant"


class ConversationEngine:
    def __init__(self):
        self.handlers: Dict[Intent, Callable[[str], str]] = {}
        self.intent_parser = IntentParser()

    def register_handler(self, intent: Intent, handler: Callable[[str], str]) -> None:
        self.handlers[intent] = handler

    @staticmethod
    def _is_coding_query(text: str) -> bool:
        keywords = (
            "code", "function", "python", "bug", "error",
            "optimize", "logic", "algorithm", "class",
            "api", "async", "database", "sql", "javascript"
        )
        text = text.lower()
        return any(k in text for k in keywords)

    def process(self, query: str, security_manager=None, memory=None) -> str:
        try:
            intent, confidence = self.intent_parser.parse(query)

            # EXIT → no memory pollution
            if intent == Intent.EXIT:
                return Intent.EXIT

            # 🔐 Security gate
            if security_manager and self.intent_parser.requires_security(intent):
                if security_manager.is_locked():
                    return "System locked hai. Pehle unlock karo."

            # 🧠 Store user message
            if memory:
                memory.add_message(ROLE_USER, query)

            # 🔥 CODING QUERIES → LLM FIRST (override intent)
            if self._is_coding_query(query):
                reply = ask_llm(
                    f"Answer like a senior developer. Be concise and code-first.\n{query}",
                    memory
                )
                if memory:
                    memory.add_message(ROLE_ASSISTANT, reply)
                return reply

            # 🧠 Conversation-first routing
            if intent == Intent.CONVERSATION or confidence < CONFIDENCE_THRESHOLD:
                reply = ask_llm(query, memory)
                if memory:
                    memory.add_message(ROLE_ASSISTANT, reply)
                return reply

            # 🛠 Command handling (only when clearly intended)
            handler = self.handlers.get(intent)
            if handler:
                response = handler(query)
                response = response if response else "Done."

                if memory:
                    memory.add_message(ROLE_ASSISTANT, response)

                return response

            # 🤖 Fallback → LLM
            reply = ask_llm(query, memory)
            if memory:
                memory.add_message(ROLE_ASSISTANT, reply)
            return reply

        except Exception as e:
            print("ConversationEngine error:", e)
            return "Command process karte waqt error aaya."
