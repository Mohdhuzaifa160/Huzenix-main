import json
from pathlib import Path
from collections import deque
from typing import Dict, List

MAX_CONTEXT = 12  # last N messages only


class MemoryManager:
    """
    Hybrid memory system for Huzenix.
    - Short-term: conversation context (RAM only)
    - Long-term: profile + facts (persistent)
    """

    def __init__(self, data_dir: Path):
        self.file = data_dir / "memory.json"

        # long-term
        self.profile: Dict[str, str] = {}
        self.facts: List[str] = []

        # short-term (session only)
        self.context = deque(maxlen=MAX_CONTEXT)

        self._load()

    # ---------- LOAD / SAVE ---------- #

    def _load(self):
        if self.file.exists():
            try:
                data = json.loads(self.file.read_text())
                self.profile = data.get("profile", {})
                self.facts = data.get("facts", [])
            except Exception:
                pass

    def save(self):
        data = {
            "profile": self.profile,
            "facts": self.facts,
        }
        self.file.write_text(json.dumps(data, indent=2))

    # ---------- SHORT TERM (SESSION) ---------- #

    def add_message(self, role: str, content: str):
        """
        role: 'user' | 'assistant'
        """
        self.context.append({
            "role": role,
            "content": content
        })

    def get_context(self) -> List[Dict[str, str]]:
        return list(self.context)

    def clear_context(self):
        self.context.clear()

    # ---------- PROFILE ---------- #

    def set_profile(self, key: str, value: str):
        self.profile[key] = value
        self.save()

    def get_profile(self) -> Dict[str, str]:
        return self.profile

    # ---------- FACTS ---------- #

    def remember_fact(self, fact: str):
        if fact not in self.facts:
            self.facts.append(fact)
            self.save()

    def get_facts(self) -> List[str]:
        return self.facts
