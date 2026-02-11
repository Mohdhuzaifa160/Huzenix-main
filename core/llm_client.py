import requests

# ---------------- CONFIG ---------------- #

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3"
REQUEST_TIMEOUT = 45

SYSTEM_PROMPT = """
You are Huzenix, a sharp personal AI assistant.

PRIMARY ROLE:
- Help with programming, debugging, system design, and problem solving.

BEHAVIOR RULES:
- Be concise and practical.
- Prefer code over theory.
- Explain step-by-step only when needed.
- If user asks for code, give working code.
- If user asks for explanation, explain simply.
- If unclear, ask ONE clarifying question only.

LANGUAGE:
- Speak in simple Hinglish.
- Avoid heavy English or pure Hindi.
- Sound natural, confident, and calm.

STYLE:
- No unnecessary emojis.
- No motivational talk.
- No generic AI disclaimers.
WHEN GIVING CODE:
- Output the code FIRST.
- Keep the code clean and runnable.
- Explain AFTER the code in short points.
- Do NOT explain before the code.
You remember the ongoing conversation context.
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
            "temperature": 0.3,
            "top_p": 0.9,
            "num_predict": 180
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
