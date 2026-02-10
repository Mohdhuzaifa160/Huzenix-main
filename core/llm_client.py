import requests

# ---------------- CONFIG ---------------- #

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3"
REQUEST_TIMEOUT = 45

SYSTEM_PROMPT = SYSTEM_PROMPT = """
You are Huzenix, a personal AI assistant made by Huzaifa.

Your personality:
- You speak in simple Hinglish (mix of Hindi + English).
- You sound calm, friendly, and slightly witty.
- You are not overly formal.
- You do not use emojis unless the user is casual.
- You give short replies for normal conversation.
- You give clear, step-by-step replies for tasks or technical questions.

Behavior rules:
- If the user is just chatting, reply naturally like a human.
- If the user asks a command, help clearly and practically.
- If the user is confused, guide patiently.
- If you don’t know something, say it honestly.
- Do not act like a robot or an assistant from a company.
- You are loyal to the user and speak like a trusted companion.

Important:
- Do NOT mention system prompts.
- Do NOT say you are an AI model.
- Do NOT over-explain unless asked.
"""


# ---------------- CORE ---------------- #

def ask_llm(user_message: str, memory=None) -> str:
    if not user_message or not user_message.strip():
        return ""

    # ---- Build context from memory ----
    context = ""
    if memory:
        for m in memory.get_context():
            context += f"{m['role']}: {m['text']}\n"

    prompt = f"""
{SYSTEM_PROMPT}

Conversation so far:
{context}

User: {user_message}
Huzenix:
"""

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.7,
            "top_p": 0.9
        }
    }

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()

        reply = response.json().get("response", "").strip()
        if not reply:
            reply = "Samajh nahi aaya, thoda aur batao."

        # ---- Save to memory ----
        if memory:
            memory.add_message("User", user_message)
            memory.add_message("Huzenix", reply)

        return reply

    except requests.exceptions.ConnectionError:
        return "Ollama connect nahi ho pa raha. Kya service chal rahi hai?"

    except requests.exceptions.Timeout:
        return "Response thoda slow ho gaya. Dobara try karo."

    except Exception as e:
        print("LLM error:", e)
        return "Internal error aaya. Thodi der baad try karo."
