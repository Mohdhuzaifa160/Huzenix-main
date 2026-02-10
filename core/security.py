"""
Security module for Huzenix.
Manages locked/unlocked state and access control.
"""

from pathlib import Path
import json
from typing import Optional


class SecurityManager:
    """Manages system security state."""

    def __init__(self, data_dir: Path = None):
        """
        Initialize security manager.

        Args:
            data_dir: Directory for security state file
        """
        if data_dir is None:
            data_dir = Path(__file__).parent.parent / "data"
        
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.state_file = self.data_dir / "security.json"
        self._state = self._load_state()

    def _load_state(self) -> dict:
        """Load security state from file."""
        if self.state_file.exists():
            try:
                with open(self.state_file, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {"locked": False, "password_hash": None}

    def _save_state(self) -> None:
        """Save security state to file."""
        with open(self.state_file, "w") as f:
            json.dump(self._state, f, indent=2)

    def is_locked(self) -> bool:
        """Check if system is locked."""
        return self._state.get("locked", False)

    def lock(self) -> None:
        """Lock the system."""
        self._state["locked"] = True
        self._save_state()

    def unlock(self) -> None:
        """Unlock the system."""
        self._state["locked"] = False
        self._save_state()

    def set_password(self, password_hash: str) -> None:
        """Store password hash (NOT the password itself)."""
        self._state["password_hash"] = password_hash
        self._save_state()

    def verify_password(self, password_hash: str) -> bool:
        """Verify password hash."""
        stored_hash = self._state.get("password_hash")
        return stored_hash == password_hash if stored_hash else False

    def allow_operation(self, sensitive: bool) -> bool:
        """
        Check if operation is allowed.

        Args:
            sensitive: True if operation requires unlocked state

        Returns:
            True if operation is allowed
        """
        if not sensitive:
            return True
        return not self.is_locked()
