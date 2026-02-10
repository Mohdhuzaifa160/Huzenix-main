"""Huzenix modules package."""

from modules.reminders import ReminderManager
from modules.notes import NotesManager
from modules.weather import WeatherManager
from modules.calculator import Calculator
from modules.file_manager import FileManager

__all__ = [
    "ReminderManager",
    "NotesManager",
    "WeatherManager",
    "Calculator",
    "FileManager",
]
