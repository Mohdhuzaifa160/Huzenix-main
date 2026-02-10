"""
Reminders module for Huzenix.
Manages reminder creation, display, and checking.
"""

import json
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import List, Dict, Optional
import dateparser

from core.voice_output import speak
from core.voice_input import listen


class ReminderManager:
    """Manages reminders with timezone support."""

    def __init__(self, data_dir: Path = None):
        """
        Initialize reminder manager.

        Args:
            data_dir: Directory for reminder storage
        """
        if data_dir is None:
            data_dir = Path(__file__).parent.parent / "data"

        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.file = self.data_dir / "reminders.json"
        self.timezone = "Asia/Kolkata"
        self.reminders = self._load()

    def _load(self) -> List[Dict]:
        """Load reminders from file."""
        if not self.file.exists():
            return []
        try:
            with open(self.file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []

    def _save(self) -> None:
        """Save reminders to file."""
        with open(self.file, "w", encoding="utf-8") as f:
            json.dump(self.reminders, f, indent=2)

    def set_reminder(
        self,
        text: str,
        time_str: str,
        city: Optional[str] = None,
        tag: str = "uncategorized",
    ) -> bool:
        """
        Set a new reminder.

        Args:
            text: Reminder message
            time_str: Natural language time expression
            city: City/location (optional)
            tag: Category tag (default: uncategorized)

        Returns:
            True if successful, False otherwise
        """
        settings = {
            "TIMEZONE": self.timezone,
            "RETURN_AS_TIMEZONE_AWARE": True,
        }
        reminder_time = dateparser.parse(time_str, settings=settings)

        if reminder_time is None:
            speak("Sorry, I couldn't understand the reminder time.")
            return False

        # Ensure timezone-aware
        if reminder_time.tzinfo is None:
            try:
                reminder_time = reminder_time.replace(
                    tzinfo=ZoneInfo(self.timezone)
                )
            except Exception:
                speak("Could not assign timezone to the reminder time.")
                return False

        # Store in UTC for consistency
        reminder_utc = reminder_time.astimezone(ZoneInfo("UTC"))

        self.reminders.append(
            {
                "text": text,
                "time": reminder_utc.isoformat(),
                "city": city or "default (IST)",
                "tag": tag.lower(),
            }
        )

        self._save()
        formatted_time = reminder_time.strftime("%A, %d %B %Y at %I:%M %p")
        speak(
            f"Reminder set for {formatted_time} under category '{tag}'"
        )
        return True

    def _parse_iso_time(self, iso_str: str) -> Optional[datetime]:
        """Parse ISO formatted time string."""
        try:
            dt = datetime.fromisoformat(iso_str)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=ZoneInfo("UTC"))
            return dt
        except (ValueError, TypeError):
            return None

    def show_all(self) -> None:
        """Display all reminders."""
        if not self.reminders:
            speak("You have no reminders saved.")
            return

        speak(f"You have {len(self.reminders)} reminders:")
        for reminder in self.reminders:
            self._speak_reminder(reminder)

    def show_upcoming(self) -> None:
        """Display upcoming reminders."""
        now_utc = datetime.now(ZoneInfo("UTC"))
        upcoming = [
            r
            for r in self.reminders
            if (self._parse_iso_time(r.get("time", "")) or now_utc) > now_utc
        ]

        if not upcoming:
            speak("You have no upcoming reminders.")
            return

        speak(f"You have {len(upcoming)} upcoming reminders:")
        for reminder in upcoming:
            self._speak_reminder(reminder)

    def show_expired(self) -> None:
        """Display expired reminders."""
        now_utc = datetime.now(ZoneInfo("UTC"))
        expired = [
            r
            for r in self.reminders
            if (self._parse_iso_time(r.get("time", "")) or now_utc) <= now_utc
        ]

        if not expired:
            speak("You have no expired reminders.")
            return

        speak(f"You have {len(expired)} expired reminders:")
        for reminder in expired:
            self._speak_reminder(reminder)

    def show_by_tag(self, tag: str) -> None:
        """Display reminders by tag."""
        filtered = [
            r
            for r in self.reminders
            if r.get("tag", "uncategorized").lower() == tag.lower()
        ]

        if not filtered:
            speak(f"No reminders found with tag '{tag}'.")
            return

        speak(f"You have {len(filtered)} reminders with tag '{tag}':")
        for reminder in filtered:
            self._speak_reminder(reminder)

    def show_interactive(self) -> None:
        """Show reminders with user choice."""
        speak(
            "Do you want to see all reminders, upcoming, expired, or by tag?"
        )
        choice = (listen() or "").lower()

        if "upcoming" in choice:
            self.show_upcoming()
        elif "old" in choice or "expired" in choice:
            self.show_expired()
        elif "tag" in choice:
            speak("Please say the tag.")
            tag = listen() or ""
            self.show_by_tag(tag)
        else:
            self.show_all()

    def _speak_reminder(self, reminder: Dict) -> None:
        """Speak a single reminder."""
        time_dt = self._parse_iso_time(reminder.get("time", ""))
        if time_dt:
            local_time = time_dt.astimezone(ZoneInfo(self.timezone))
            formatted = local_time.strftime("%d %B %Y, %I:%M %p")
        else:
            formatted = "unknown time"

        speak(
            f"{reminder['text']} at {formatted} "
            f"in {reminder['city']} under {reminder['tag']} tag"
        )

    def check_and_trigger(self) -> None:
        """Check for triggered reminders and speak them."""
        now_utc = datetime.now(ZoneInfo("UTC"))
        to_remove = []

        for i, reminder in enumerate(self.reminders):
            reminder_time = self._parse_iso_time(reminder.get("time", ""))
            if reminder_time is None:
                continue

            if now_utc >= reminder_time:
                local_time = reminder_time.astimezone(ZoneInfo(self.timezone))
                formatted = local_time.strftime("%d %B %Y, %I:%M %p")
                speak(
                    f"Reminder: {reminder['text']} (set for {formatted} IST)"
                )
                to_remove.append(i)

        # Remove triggered reminders
        for i in reversed(to_remove):
            self.reminders.pop(i)

        if to_remove:
            self._save()

    def delete_all(self) -> None:
        """Delete all reminders."""
        self.reminders.clear()
        self._save()
        speak("All reminders have been deleted.")
