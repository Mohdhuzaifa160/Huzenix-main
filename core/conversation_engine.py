"""
Conversation engine for Huzenix.
Decides whether to route input to commands or natural conversation.
"""

from typing import Optional, Callable, Dict
from core.intent_parser import Intent, IntentParser
from core.llm_client import ask_llm

CONFIDENCE_THRESHOLD = 0.35
ROLE_USER = "user"
ROLE_ASSISTANT = "assistant"


class ConversationEngine:
    """
    Brain of Huzenix.
    - High confidence → command handlers
    - Low confidence → LLM conversation
    """

    def __init__(self):
        self.handlers: Dict[
            Intent, Callable[[str, Optional[object]], Optional[str]]
        ] = {}
        self.intent_parser = IntentParser()

    def register_handler(
        self,
        intent: Intent,
        handler: Callable[[str, Optional[object]], Optional[str]],
    ) -> None:
        self.handlers[intent] = handler

    def process(
        self,
        query: str,
        security_manager=None,
        memory=None,
    ) -> str:
        intent, confidence = self.intent_parser.parse(query)

        # 🔐 Security gate
        if security_manager and self.intent_parser.requires_security(intent):
            if security_manager.is_locked():
                return "System locked hai. Pehle unlock karo."

        # 🧠 MEMORY: store user message
        if memory:
            memory.add_message(ROLE_USER, query)

        # 🧠 DECISION: conversation vs command
        if intent == Intent.CONVERSATION or confidence < CONFIDENCE_THRESHOLD:
            reply = ask_llm(query, memory)
            if memory:
                memory.add_message(ROLE_ASSISTANT, reply)
            return reply

        # 🛠 Command handling
        handler = self.handlers.get(intent)
        if handler:
            try:
                response = handler(query, memory)
                return response if response else "Done."
            except Exception as e:
                return "Command process karte waqt error aaya."

        # 🤖 Fallback → LLM
        reply = ask_llm(query, memory)
        if memory:
            memory.add_message(ROLE_ASSISTANT, reply)
        return reply
