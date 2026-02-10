"""
Huzenix - Modular Voice AI Assistant
Main entry point (ROUTER ONLY).
"""

import time
import schedule
from pathlib import Path
from datetime import datetime
from enum import Enum, auto

# Core
from core.voice_input import listen
from core.wake_word import wait_for_wake_word
from core.voice_output import speak
from core.security import SecurityManager
from core.conversation_engine import ConversationEngine
from core.intent_parser import Intent
from core.memory_manager import MemoryManager

# Modules
from modules.reminders import ReminderManager
from modules.notes import NotesManager
from modules.weather import WeatherManager
from modules.calculator import Calculator
from modules.file_manager import FileManager

# Plugins
try:
    from plugins.chat import ChatPlugin
    CHAT_PLUGIN_AVAILABLE = True
except ImportError:
    CHAT_PLUGIN_AVAILABLE = False


class AppSignal(Enum):
    CONTINUE = auto()
    EXIT = auto()


class HuzenixApp:
    """Main application router and lifecycle manager."""

    def __init__(self):
        # Paths
        self.data_dir = Path(__file__).parent / "data"
        self.data_dir.mkdir(exist_ok=True)

        # Core managers
        self.security = SecurityManager(self.data_dir)
        self.memory = MemoryManager(self.data_dir)

        # Feature modules
        self.reminders = ReminderManager(self.data_dir)
        self.notes = NotesManager(self.data_dir)
        self.weather = WeatherManager()
        self.calculator = Calculator()
        self.file_manager = FileManager()

        # Conversation engine
        self.engine = ConversationEngine()
        self._register_handlers()
        self._load_plugins()

        # Scheduler
        schedule.every(60).seconds.do(self.reminders.check_and_trigger)

    # ---------------- ENGINE REGISTRATION ---------------- #

    def _register_handlers(self):
        self.engine.register_handler(Intent.TIME, self._time)
        self.engine.register_handler(Intent.DATE, self._date)
        self.engine.register_handler(Intent.WEATHER, self._weather)
        self.engine.register_handler(Intent.REMINDERS, self._reminders)
        self.engine.register_handler(Intent.NOTES, self._notes)
        self.engine.register_handler(Intent.CALCULATOR, self._calculator)
        self.engine.register_handler(Intent.FILES, self._files)
        self.engine.register_handler(Intent.HELP, self._help)
        self.engine.register_handler(Intent.EXIT, self._exit)

    def _load_plugins(self):
        if CHAT_PLUGIN_AVAILABLE:
            ChatPlugin().register(self.engine)

    # ---------------- PURE HANDLERS (NO I/O) ---------------- #

    def _time(self, _: str) -> str:
        return datetime.now().strftime("Abhi time %I:%M %p hai.")

    def _date(self, _: str) -> str:
        return datetime.now().strftime("Aaj %A, %d %B %Y hai.")

    def _weather(self, query: str) -> str:
        return self.weather.get_weather(query)

    def _reminders(self, query: str) -> str:
        if self.security.is_locked():
            return "Reminders ke liye system unlock karo."
        return self.reminders.handle_command(query)

    def _notes(self, query: str) -> str:
        if self.security.is_locked():
            return "Notes access karne ke liye system unlock karo."
        return self.notes.handle_command(query)

    def _calculator(self, query: str) -> str:
        return self.calculator.calculate(query)

    def _files(self, query: str) -> str:
        if self.security.is_locked():
            return "File operations ke liye system unlock karo."
        return self.file_manager.handle_command(query)

    def _help(self, _: str) -> str:
        return (
            "Tum mujhse normally baat kar sakte ho ya commands bol sakte ho.\n"
            "Examples: time, date, weather, notes, reminders, calculator, files."
        )

    def _exit(self, _: str):
        return AppSignal.EXIT

    # ---------------- MAIN LOOP ---------------- #

    def run(self):
        speak("Huzenix online hai. Wake word bolo.")

        while True:
            # 🔊 Wait for wake word (blocking)
            wait_for_wake_word()

            print("✅ Wake word detected.")
            speak("Haan, boliye.")

            while True:
                schedule.run_pending()

                query = listen()
                if not query:
                    time.sleep(0.2)
                    continue
                print("✅ Query received:", query)

                result = self.engine.process(query, self.security)

                if result == "__EXIT__":
                    speak("Goodbye. Phir milte hain.")
                    break

                if result:
                    speak(result)

                time.sleep(0.3)


if __name__ == "__main__":
    HuzenixApp().run()

