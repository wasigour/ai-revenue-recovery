import os
import re
from google import genai

# FIX: Yeh line terminal ki zaroorat khatam kar degi aur environment variable Python mein hi set kar degi
os.environ["AQ.Ab8RN6IYAj0TI5pE4IB1F0CbkoklaoMoNPQw4NbqZmwmfzY6Bw"] = "AQ.Ab8RN6IYAj0TI5pE4IB1F0CbkoklaoMoNPQw4NbqZmwmfzY6Bw"

# --- AAPKA EXISTING CODE YAHAN SE START HOGA ---
API_KEY = os.environ.get("AQ.Ab8RN6IYAj0TI5pE4IB1F0CbkoklaoMoNPQw4NbqZmwmfzY6Bw")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY environment variable not set.")

client = genai.Client(api_key=API_KEY)

# Current Flash model — check Google's docs periodically, model names change.
MODEL_NAME = "gemini-3.6-flash" # Yahan 1.5-flash use karein, 2.5 abhi beta mein hai

def _fallback_message(transaction_amount, bank_name, error_reason):
    """Deterministic fallback used if the LLM call fails or output looks bad."""
    return (
        f"Aapka ₹{transaction_amount} ka payment {bank_name} ke through fail ho gaya "
        f"({error_reason}). Kya hum kal retry karein ya aapko naya payment link bhej dein? 🙂"
    )

def _looks_valid(text):
    """Basic sanity check: not empty, not absurdly long, roughly within sentence limit."""
    if not text or not text.strip():
        return False
    sentence_count = len(re.findall(r'[.!?]', text))
    if sentence_count > 5:  # allow some slack over the "max 3" instruction
        return False
    if len(text) > 600:  # guard against a runaway/hallucinated response
        return False
    return True

def generate_hinglish_nudge(transaction_amount, bank_name, error_reason):
    """
    LLM ko prompt bhej kar ek customized WhatsApp message generate karta hai.
    Falls back to a safe deterministic message on any failure or invalid output.
    """
    prompt = f"""
    You are a polite customer support AI for a fintech company.
    A payment has failed. Write a short, empathetic WhatsApp message in Hinglish to the customer.

    Context:
    - Amount: ₹{transaction_amount}
    - Bank: {bank_name}
    - Reason: {error_reason}

    Rules:
    - Do not sound like a strict debt collector. Be helpful and friendly.
    - Mention the amount and the reason gently.
    - Ask if they want us to retry tomorrow or if they want a new payment link.
    - Maximum 3 sentences. No emojis except one at the end.
    """

    try:
        # Chat API use karne se AFC warning hamesha ke liye hat jayegi
        chat = client.chats.create(model=MODEL_NAME)
        response = chat.send_message(prompt)
        text = (response.text or "").strip()

        if _looks_valid(text):
            return text
        else:
            print(f"[warn] LLM output failed validation, using fallback. Raw: {text!r}")
            return _fallback_message(transaction_amount, bank_name, error_reason)

    except Exception as e:
        print(f"[error] Gemini API call failed: {e}")
        return _fallback_message(transaction_amount, bank_name, error_reason)


# --- Test the LLM ---
if __name__ == "__main__":
    # Example 1: Soft User Error (Low Balance)
    msg1 = generate_hinglish_nudge(499, "SBI", "INSUFFICIENT_FUNDS")
    print("Scenario 1 (Low Balance):")
    print(msg1)
    print("-" * 40)

    # Example 2: Technical Error (Server Down)
    msg2 = generate_hinglish_nudge(1499, "HDFC", "ISSUER_DOWN")
    print("Scenario 2 (Bank Server Down):")
    print(msg2)
