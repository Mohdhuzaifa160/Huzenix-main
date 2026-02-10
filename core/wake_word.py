import time
import queue
import numpy as np
import sounddevice as sd
import speech_recognition as sr
from core.voice_output import speak

# ---------------- CONFIG ---------------- #

SAMPLE_RATE = 16000
SILENCE_THRESHOLD = 0.003

WAKE_WORDS = (
    "hello"
)

print("✅ Using sounddevice for voice input")

# ---------------- CORE LISTEN ---------------- #

def listen(timeout: float = 5.0, phrase_time_limit: float = 6.0) -> str:
    return _listen_sounddevice(timeout, phrase_time_limit)

# ---------------- SOUNDDEVICE LISTEN ---------------- #

def _listen_sounddevice(timeout: float, phrase_time_limit: float) -> str:
    recognizer = sr.Recognizer()
    audio_queue = queue.Queue()

    def callback(indata, frames, time_info, status):
        audio_queue.put(indata.copy())

    print("🎤 Listening...")
    try:
        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="float32",
            callback=callback,
        ):
            frames = []
            start = time.time()

            while time.time() - start < phrase_time_limit:
                try:
                    frames.append(audio_queue.get(timeout=0.5))
                except queue.Empty:
                    pass

        if not frames:
            return ""

        audio_np = np.concatenate(frames, axis=0)

        # 🔇 Silence detection (float domain)
        if np.mean(np.abs(audio_np)) < 0.0008:
            return ""

        # convert to int16 for speech_recognition
        audio_np = np.clip(audio_np, -1.0, 1.0)
        audio_np = (audio_np * 32767).astype(np.int16)

        audio_data = sr.AudioData(
            audio_np.tobytes(),
            SAMPLE_RATE,
            2
        )

        text = recognizer.recognize_google(audio_data, language="hi-IN")
        print("You:", text)
        return text.lower()

    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        speak("Speech service unavailable.")
        return ""
    except Exception as e:
        print("Sounddevice error:", e)
        return ""

# ---------------- WAKE WORD ---------------- #

def wait_for_wake_word():
    """
    Low-power wake-word listener.
    """
    print("🎧 Huzenix standby mode")

    while True:
        text = listen(timeout=2.0, phrase_time_limit=2.0)

        if not text:
            time.sleep(0.25)
            continue

        if len(text.split()) > 4:
            continue

        for word in WAKE_WORDS:
            if word in text:
                speak("Yes?")
                return
