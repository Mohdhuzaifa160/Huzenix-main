import queue
import json
import time
import sounddevice as sd
from vosk import Model, KaldiRecognizer

SAMPLE_RATE = 16000
BLOCK_SIZE = 8000
VOSK_MODEL_PATH = "models/vosk/vosk-model-small-en-us-0.15"
WAKE_WORDS = ("hello", "huzenix", "hey huzenix")


class STTEngine:
    """
    Conversational STT Engine
    - Wake word switches mode
    - Continuous listening after wake
    """

    def __init__(self):
        self.audio_queue = queue.Queue()
        self.model = Model(VOSK_MODEL_PATH)
        self.recognizer = None
        self.stream = None

    # ---------- AUDIO ---------- #

    def _callback(self, indata, frames, time_info, status):
        self.audio_queue.put(bytes(indata))

    def _start_stream(self):
        if self.stream:
            return

        self.stream = sd.RawInputStream(
            samplerate=SAMPLE_RATE,
            blocksize=BLOCK_SIZE,
            dtype="int16",
            channels=1,
            callback=self._callback,
        )
        self.stream.start()
        self.recognizer = KaldiRecognizer(self.model, SAMPLE_RATE)
        print("🎧 STT stream started")

    def _stop_stream(self):
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
            print("🛑 STT stream stopped")

    def _reset(self):
        self.recognizer = KaldiRecognizer(self.model, SAMPLE_RATE)
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break

    # ---------- PUBLIC API ---------- #

    def wait_for_wake(self):
        """Blocks until wake word detected"""
        self._start_stream()
        print("🛌 Waiting for wake word...")

        while True:
            data = self.audio_queue.get()
            if self.recognizer.AcceptWaveform(data):
                result = json.loads(self.recognizer.Result())
                text = result.get("text", "").lower().strip()
                if not text:
                    continue

                words = text.split()
                if any(w == word for w in WAKE_WORDS for word in words):
                    print("Wake word detected:", text)
                    self._reset()
                    return

    def listen_once(self, timeout=6) -> str:
        """Listen for ONE sentence (conversation mode)"""
        start = time.time()

        while True:
            if time.time() - start > timeout:
                return ""

            data = self.audio_queue.get()
            if self.recognizer.AcceptWaveform(data):
                result = json.loads(self.recognizer.Result())
                text = result.get("text", "").lower().strip()
                if text:
                    print("🗣 Heard:", text)
                    return text
