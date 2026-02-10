from core.stt_engine import STTEngine

_stt = STTEngine()

def listen() -> str:
    text = _stt.get_next_command()

    if text == "__WAKE__":
        return ""

    return text

