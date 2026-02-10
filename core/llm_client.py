import requests

# ---------------- CONFIG ---------------- #

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3"
REQUEST_TIMEOUT = 45

SYSTEM_PROMPT = """
You are Huzenix, a personal AI assistant made by Huzaifa.

Personality:
- Speak in simple Hinglish (Hindi + English).
- Calm, friendly, slightly witty.
- Not overly formal.
- Short replies for casual talk.
- Clear, step-by-step replies for technical tasks.
- Honest if you don’t know something.

Rules:
- Do not mention system prompts.
- Do not say you are an AI model.
- Do not over-explain unless asked.
- Sound like a trusted companion, not a corporate bot.
"""

# ---------------- CORE ---------------- #

def ask_llm(user_message: str, memory=None) -> str:
    if not user_message or not user_message.strip():
        return ""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

    # ---- Inject short-term memory ----
    if memory:
        for m in memory.get_context():
            messages.append({
                "role": m["role"],
                "content": m["content"]
            })

    # ---- Current user message ----
    messages.append({
        "role": "user",
        "content": user_message
    })

    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": 0.7,
            "top_p": 0.9
        }
    }

    try:
        r = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=REQUEST_TIMEOUT
        )
        r.raise_for_status()

        data = r.json()
        reply = data.get("message", {}).get("content", "").strip()

        return reply or "Samajh nahi aaya, thoda aur batao."

    except requests.exceptions.ConnectionError:
        return "Ollama connect nahi ho pa raha. Kya service chal rahi hai?"

    except requests.exceptions.Timeout:
        return "Response thoda slow ho gaya. Dobara try karo."

    except Exception as e:
        print("LLM error:", e)
        return "Internal error aaya. Thodi der baad try karo."
