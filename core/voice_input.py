"""
Voice input interface for Huzenix.
Thin wrapper over STTEngine.
"""

from core.stt_engine import STTEngine

_stt = STTEngine()

def wait_for_wake():
    _stt.wait_for_wake()

def listen():
    return _stt.listen_once()
