import json
import queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer
from core.voice_output import speak

SAMPLE_RATE = 16000
WAKE_WORDS = ("hello", "huzenix")

MODEL_PATH = "models/vosk-model-small-en-in-0.4"

audio_queue = queue.Queue()

model = Model(MODEL_PATH)
recognizer = KaldiRecognizer(model, SAMPLE_RATE)


def _callback(indata, frames, time, status):
    audio_queue.put(bytes(indata))


def wait_for_wake_word():
    """
    ALWAYS-ON wake word listener (stable).
    """
    print("🎧 Huzenix standby mode")

    with sd.RawInputStream(
        samplerate=SAMPLE_RATE,
        blocksize=8000,
        dtype="int16",
        channels=1,
        callback=_callback,
    ):
        while True:
            data = audio_queue.get()
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "").lower()

                if not text:
                    continue

                print("Wake heard:", text)

                for word in WAKE_WORDS:
                    if word in text:
                        speak("Yes?")
                        return
