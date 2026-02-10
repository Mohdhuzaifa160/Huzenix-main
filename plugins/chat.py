"""
OpenAI chat plugin for Huzenix.
Optional plugin for advanced conversational AI.
"""

from plugins.base import HuzenixPlugin
from core.intent_parser import Intent
import os


class ChatPlugin(HuzenixPlugin):
    """OpenAI-powered chat plugin."""

    @property
    def name(self) -> str:
        return "ChatPlugin"

    @property
    def intents(self) -> list:
        return [Intent.CONVERSATION]

    def handle(self, query: str) -> str:
        """
        Handle chat requests via OpenAI.

        Args:
            query: User query

        Returns:
            Chat response
        """
        try:
            from openai import OpenAI
            
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                return "OpenAI API key not configured."
            
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are Huzenix, a helpful AI assistant."},
                    {"role": "user", "content": query}
                ],
                max_tokens=150
            )
            return response.choices[0].message.content
        except ImportError:
            return "OpenAI library not installed."
        except Exception as e:
            return f"Chat service error: {str(e)}"
