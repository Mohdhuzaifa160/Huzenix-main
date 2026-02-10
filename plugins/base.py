"""
Plugin system for Huzenix.
Provides base class and registration mechanism for plugins.
"""

from abc import ABC, abstractmethod
from core.intent_parser import Intent


class HuzenixPlugin(ABC):
    """Base class for Huzenix plugins."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name."""
        pass

    @property
    @abstractmethod
    def intents(self) -> list:
        """List of Intent values this plugin handles."""
        pass

    @abstractmethod
    def handle(self, query: str) -> str:
        """
        Handle a query for this plugin's intents.

        Args:
            query: User query

        Returns:
            Response string
        """
        pass

    def register(self, engine) -> None:
        """
        Register this plugin with conversation engine.

        Args:
            engine: ConversationEngine instance
        """
        for intent in self.intents:
            engine.register_handler(intent, self.handle)
