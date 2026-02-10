"""
File manager module for Huzenix.
Handles file creation, deletion, reading, and listing.
"""

from pathlib import Path
from typing import List, Optional

from core.voice_output import speak


class FileManager:
    """Manages file operations."""

    def __init__(self, base_dir: str = "."):
        """
        Initialize file manager.

        Args:
            base_dir: Base directory for operations (default: current)
        """
        self.base_dir = Path(base_dir)

    def _clean_filename(self, name: str) -> str:
        """
        Clean and normalize filename.

        Args:
            name: Raw filename

        Returns:
            Cleaned filename
        """
        name = name.strip().strip('"').strip("'")

        # Remove common prefixes
        prefixes = ("named ", "called ", "the ")
        for prefix in prefixes:
            if name.lower().startswith(prefix):
                name = name[len(prefix) :].strip()

        return name

    def create_file(self, filename: str) -> bool:
        """
        Create a new file.

        Args:
            filename: Path/name of file to create

        Returns:
            True if successful, False otherwise
        """
        filename = self._clean_filename(filename)
        if not filename:
            speak("Please provide a filename to create.")
            return False

        try:
            filepath = self.base_dir / filename
            filepath.parent.mkdir(parents=True, exist_ok=True)
            filepath.touch()
            speak(f"File {filename} created.")
            return True

        except Exception as e:
            speak(f"Error creating file: {e}")
            print(f"Create file error: {e}")
            return False

    def delete_file(self, filename: str) -> bool:
        """
        Delete a file.

        Args:
            filename: Path/name of file to delete

        Returns:
            True if successful, False otherwise
        """
        filename = self._clean_filename(filename)
        if not filename:
            speak("Please provide a filename to delete.")
            return False

        try:
            filepath = self.base_dir / filename
            if filepath.exists():
                filepath.unlink()
                speak(f"File {filename} deleted.")
                return True
            else:
                speak("File not found.")
                return False

        except Exception as e:
            speak(f"Error deleting file: {e}")
            print(f"Delete file error: {e}")
            return False

    def list_files(self) -> bool:
        """
        List files in base directory.

        Returns:
            True if successful, False otherwise
        """
        try:
            files = [f.name for f in self.base_dir.iterdir() if f.is_file()]

            if files:
                speak(f"Files in directory: {', '.join(files)}")
                return True
            else:
                speak("No files found in the current directory.")
                return False

        except Exception as e:
            speak(f"Error listing files: {e}")
            print(f"List files error: {e}")
            return False

    def read_file(self, filename: str) -> bool:
        """
        Read and speak file contents.

        Args:
            filename: Path/name of file to read

        Returns:
            True if successful, False otherwise
        """
        filename = self._clean_filename(filename)
        if not filename:
            speak("Please provide a filename to read.")
            return False

        try:
            filepath = self.base_dir / filename
            if filepath.exists():
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read().strip()

                if content:
                    speak(f"Content of {filename}: {content}")
                    return True
                else:
                    speak(f"{filename} is empty.")
                    return False
            else:
                speak("File not found.")
                return False

        except Exception as e:
            speak(f"Error reading file: {e}")
            print(f"Read file error: {e}")
            return False

    def rename_file(self, old_name: str, new_name: str) -> bool:
        """
        Rename a file.

        Args:
            old_name: Current filename
            new_name: New filename

        Returns:
            True if successful, False otherwise
        """
        old_name = self._clean_filename(old_name)
        new_name = self._clean_filename(new_name)

        if not old_name or not new_name:
            speak("Please specify both old and new filenames.")
            return False

        try:
            old_path = self.base_dir / old_name
            new_path = self.base_dir / new_name

            if old_path.exists():
                new_path.parent.mkdir(parents=True, exist_ok=True)
                old_path.rename(new_path)
                speak(f"File renamed from {old_name} to {new_name}")
                return True
            else:
                speak("Original file not found.")
                return False

        except Exception as e:
            speak(f"Error renaming file: {e}")
            print(f"Rename file error: {e}")
            return False

    def handle_command(self, command: str) -> bool:
        """
        Handle file management command.

        Args:
            command: User command

        Returns:
            True if successful, False otherwise
        """
        cmd_lower = command.lower().strip()

        if cmd_lower.startswith("create file"):
            filename = command[len("create file") :].strip()
            return self.create_file(filename)

        elif cmd_lower.startswith("delete file"):
            filename = command[len("delete file") :].strip()
            return self.delete_file(filename)

        elif cmd_lower.startswith("read file"):
            filename = command[len("read file") :].strip()
            return self.read_file(filename)

        elif cmd_lower.startswith("rename file"):
            rest = command[len("rename file") :].strip()
            parts = rest.split(" to ")
            if len(parts) == 2:
                return self.rename_file(parts[0], parts[1])
            else:
                speak(
                    "Please use format: rename file OLD to NEW"
                )
                return False

        elif "list" in cmd_lower:
            return self.list_files()

        else:
            speak("File command not recognized.")
            return False
