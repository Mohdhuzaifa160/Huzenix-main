import subprocess
import os
import sounddevice as sd
import soundfile as sf
import tempfile

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

PIPER_EXE = os.path.join(BASE_DIR, "tools", "piper", "piper.exe")
VOICE_MODEL = os.path.join(BASE_DIR, "tools", "piper", "models", "en_US-amy-medium.onnx")

SAMPLE_RATE = 22050


def speak(text: str):
    if not text.strip():
        return

    print("Huzenix:", text)

    if os.path.exists(PIPER_EXE) and os.path.exists(VOICE_MODEL):
        _speak_piper(text)
    else:
        print("⚠ Piper not found, text only.")


def _speak_piper(text: str):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            wav_path = f.name

        cmd = [
            PIPER_EXE,
            "--model", VOICE_MODEL,
            "--output_file", wav_path,
            "--length_scale", "1.05"
        ]

        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            text=True
        )

        process.communicate(input=text)

        data, sr = sf.read(wav_path, dtype="float32")
        sd.play(data, sr)
        sd.wait()

        os.remove(wav_path)

    except Exception as e:
        print("TTS error:", e)
