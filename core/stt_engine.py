import queue
import json
import time
import numpy as np
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import whisper

SAMPLE_RATE = 16000
BLOCK_SIZE = 8000
VOSK_MODEL_PATH = "models/vosk/vosk-model-small-en-us-0.15"

WAKE_WORDS = ("hello", "huzenix", "hey huzenix","hello")


class STTEngine:
    def __init__(self):
        self.audio_queue = queue.Queue()
        self.vosk_model = Model(VOSK_MODEL_PATH)
        self.vosk_recognizer = KaldiRecognizer(self.vosk_model, SAMPLE_RATE)
        self.whisper_model = whisper.load_model("small")
        self.active = False

        self.stream = sd.RawInputStream(
            samplerate=SAMPLE_RATE,
            blocksize=BLOCK_SIZE,
            dtype="int16",
            channels=1,
            callback=self._callback,
        )
        self.stream.start()

        print("🎧 STT Engine started (Vosk + Whisper)")

    def _callback(self, indata, frames, time_info, status):
        self.audio_queue.put(bytes(indata))

    def get_next_command(self) -> str:
        """
        Blocking call.
        Returns command AFTER wake word.
        """
        collected_audio = []
        start_time = time.time()

        while True:
            data = self.audio_queue.get()

            if self.vosk_recognizer.AcceptWaveform(data):
                result = json.loads(self.vosk_recognizer.Result())
                text = result.get("text", "").strip().lower()

                if not text:
                    continue

                print("🗣 Heard:", text)

                # 💤 Wake mode
                if not self.active:
                    if any(w in text for w in WAKE_WORDS):
                        self.active = True
                        self._flush_queue()
                        return "__WAKE__"
                    continue

                # 🧠 Active command
                return text

            # safety timeout (5 sec silence)
            if time.time() - start_time > 5:
                self._flush_queue()
                return ""

    def _flush_queue(self):
        """Clear leftover audio."""
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break

    def transcribe_long(self, audio_np: np.ndarray) -> str:
        """
        Whisper transcription for long speech.
        """
        audio_np = np.clip(audio_np, -1.0, 1.0)
        result = self.whisper_model.transcribe(
            audio_np,
            language="hi",
            fp16=False,
        )
        return result["text"].strip().lower()
