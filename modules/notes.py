"""
Notes module for Huzenix.
Manages note creation, reading, and deletion.
"""

from pathlib import Path
from datetime import datetime
from typing import List

from core.voice_output import speak
from core.voice_input import listen


class NotesManager:
    """Manages user notes."""

    def __init__(self, data_dir: Path = None):
        """
        Initialize notes manager.

        Args:
            data_dir: Directory for note storage
        """
        if data_dir is None:
            data_dir = Path(__file__).parent.parent / "data"

        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.file = self.data_dir / "notes.txt"

    def take_note(self) -> bool:
        """
        Capture a note from user input.

        Returns:
            True if note was saved, False otherwise
        """
        speak("What should I write?")
        note = listen()

        if not note:
            speak("No note content provided.")
            return False

        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(self.file, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] {note}\n")
            speak("Note saved successfully.")
            return True
        except IOError as e:
            speak("Sorry, I couldn't save the note.")
            print(f"Error saving note: {e}")
            return False

    def read_notes(self) -> bool:
        """
        Read and speak all notes.

        Returns:
            True if notes were read, False otherwise
        """
        if not self.file.exists():
            speak("You don't have any notes yet.")
            return False

        try:
            with open(self.file, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()]

            if not lines:
                speak("You don't have any notes.")
                return False

            speak(f"You have {len(lines)} notes:")
            for line in lines:
                print(line)
                speak(line)

            return True
        except IOError as e:
            speak("Sorry, I couldn't read your notes.")
            print(f"Error reading notes: {e}")
            return False

    def delete_all(self) -> bool:
        """
        Delete all notes after confirmation.

        Returns:
            True if notes were deleted, False otherwise
        """
        if not self.file.exists():
            speak("You don't have any notes to delete.")
            return False

        try:
            speak("Are you sure you want to delete all notes? Say yes to confirm.")
            confirmation = listen().lower() if listen() else ""

            if "yes" in confirmation:
                with open(self.file, "w", encoding="utf-8") as f:
                    f.truncate(0)
                speak("All your notes have been deleted.")
                return True
            else:
                speak("Deletion cancelled.")
                return False

        except IOError as e:
            speak("Sorry, I couldn't delete the notes.")
            print(f"Error deleting notes: {e}")
            return False

    def get_notes(self) -> List[str]:
        """
        Get all notes as a list.

        Returns:
            List of note strings
        """
        if not self.file.exists():
            return []

        try:
            with open(self.file, "r", encoding="utf-8") as f:
                return [line.strip() for line in f if line.strip()]
        except IOError:
            return []
