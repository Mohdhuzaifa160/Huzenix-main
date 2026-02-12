import queue
import json
import time
import sounddevice as sd
from vosk import Model, KaldiRecognizer

SAMPLE_RATE = 16000
BLOCK_SIZE = 8000
VOSK_MODEL_PATH = "models/vosk/vosk-model-small-en-in-0.4"
WAKE_WORDS = ("hello", "huzenix", "hey huzenix")


class STTEngine:
    def __init__(self):
        self.audio_queue = queue.Queue()
        self.model = Model(VOSK_MODEL_PATH)
        self.recognizer = KaldiRecognizer(self.model, SAMPLE_RATE)

        # 🔥 Stream always ON (low latency)
        self.stream = sd.RawInputStream(
            samplerate=SAMPLE_RATE,
            blocksize=BLOCK_SIZE,
            dtype="int16",
            channels=1,
            callback=self._callback,
        )
        self.stream.start()

        print("🎧 STT stream started (low latency mode)")

    def _callback(self, indata, frames, time_info, status):
        self.audio_queue.put(bytes(indata))

    def _reset(self):
        self.recognizer = KaldiRecognizer(self.model, SAMPLE_RATE)
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break

    # ---------- WAKE ---------- #

    def wait_for_wake(self):
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

    # ---------- LISTEN ---------- #

    def listen_once(self, timeout=2.5):
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
