"""
Conversation engine for Huzenix.
Decides whether to route input to commands or natural conversation.
"""

from typing import Callable, Dict
from core.intent_parser import Intent, IntentParser
from core.llm_client import ask_llm

CONFIDENCE_THRESHOLD = 0.45  # ⬅ slightly relaxed
ROLE_USER = "user"
ROLE_ASSISTANT = "assistant"


class ConversationEngine:
    """
    Brain of Huzenix.
    - Conversation-first
    - Commands only when confidence is clear
    """

    def __init__(self):
        self.handlers: Dict[Intent, Callable[[str], str]] = {}
        self.intent_parser = IntentParser()

    def register_handler(self, intent: Intent, handler: Callable[[str], str]) -> None:
        self.handlers[intent] = handler

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

            # 🧠 Store user message (non-exit)
            if memory:
                memory.add_message(ROLE_USER, query)

            # 🧠 Conversation FIRST
            if intent == Intent.CONVERSATION or confidence < CONFIDENCE_THRESHOLD:
                reply = ask_llm(query, memory)
                if memory:
                    memory.add_message(ROLE_ASSISTANT, reply)
                return reply

            # 🛠 Command handling
            handler = self.handlers.get(intent)
            if handler:
                response = handler(query)
                response = response if response else "Done."

                # ✅ Store command response too
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
