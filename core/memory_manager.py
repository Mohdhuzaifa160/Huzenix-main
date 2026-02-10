import json
from pathlib import Path
from typing import Dict, List


class MemoryManager:
    """
    Simple persistent memory for Huzenix.
    Stores user facts + short conversation context.
    """

    def __init__(self, data_dir: Path):
        self.file = data_dir / "memory.json"
        self.data = {
            "profile": {},
            "facts": [],
            "recent_messages": []
        }
        self._load()

    def _load(self):
        if self.file.exists():
            try:
                self.data.update(json.loads(self.file.read_text()))
            except Exception:
                pass

    def _save(self):
        self.file.write_text(json.dumps(self.data, indent=2))

    # -------- PROFILE --------

    def set_profile(self, key: str, value: str):
        self.data["profile"][key] = value
        self._save()

    def get_profile(self) -> Dict[str, str]:
        return self.data["profile"]

    # -------- FACTS --------

    def remember_fact(self, fact: str):
        if fact not in self.data["facts"]:
            self.data["facts"].append(fact)
            self._save()

    def get_facts(self) -> List[str]:
        return self.data["facts"]

    # -------- CONTEXT --------

    def add_message(self, role: str, text: str, limit: int = 5):
        self.data["recent_messages"].append(
            {"role": role, "text": text}
        )
        self.data["recent_messages"] = self.data["recent_messages"][-limit:]
        self._save()

    def get_context(self) -> List[Dict[str, str]]:
        return self.data["recent_messages"]
