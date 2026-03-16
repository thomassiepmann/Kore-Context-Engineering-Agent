import httpx
import os

CHUTES_BASE_URL = "https://llm.chutes.ai/v1"
# Qwen3-235B-A22B: 262k Kontext, top Instruction-Following für Context Engineering Agenten
# Fallback: "deepseek-ai/DeepSeek-R1" für Reasoning-intensive Tasks
CHUTES_MODEL = "Qwen/Qwen3-235B-A22B"
CHUTES_API_KEY = os.getenv("CHUTES_API_KEY", "")

def chat(messages: list, system: str = "", temperature: float = 0.3, max_tokens: int = 1500) -> str:
    if not CHUTES_API_KEY:
        return "[FEHLER] CHUTES_API_KEY nicht gesetzt."
    payload = {"model": CHUTES_MODEL, "messages": messages,
               "temperature": temperature, "max_tokens": max_tokens}
    if system:
        payload["messages"] = [{"role": "system", "content": system}] + messages
    try:
        response = httpx.post(f"{CHUTES_BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {CHUTES_API_KEY}", "Content-Type": "application/json"},
            json=payload, timeout=60.0)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except httpx.HTTPStatusError as e:
        return f"[API FEHLER] {e.response.status_code}: {e.response.text}"
    except Exception as e:
        return f"[FEHLER] {str(e)}"

def summarize(text: str, topic: str = "") -> str:
    system = ("Du bist ein präziser Assistent der wissenschaftliche Texte auf Deutsch zusammenfasst. "
              "Fokus: Praktische Anwendbarkeit für AI-Entwicklung und Context Engineering. "
              "Antworte immer auf Deutsch. Maximal 200 Wörter.")
    prompt = f"Fasse diesen Text zusammen{' (Thema: ' + topic + ')' if topic else ''}:\n\n{text[:3000]}"
    return chat([{"role": "user", "content": prompt}], system=system, temperature=0.2)

def improve_prompt_template(template: str, feedback_examples: list) -> str:
    system = ("Du bist ein Prompt-Optimierer. Verbessere das Template basierend auf Feedback. "
              "Antworte NUR mit dem verbesserten Template — kein Kommentar.")
    examples_text = "\n".join([f"- Qualität {ex['quality']}/5: {ex.get('notes','')}" for ex in feedback_examples[:5]])
    prompt = f"Template:\n{template}\n\nFeedback:\n{examples_text}\n\nVerbessertes Template:"
    return chat([{"role": "user", "content": prompt}], system=system, temperature=0.4)

def generate_questions(project_name: str, user_input: str, context_summary: str) -> str:
    system = ("Du bist KORE. Stelle 3 Klärungsfragen die helfen einen besseren Claude-Prompt zu bauen. "
              "Antworte auf Deutsch. Format: nummerierte Liste.")
    prompt = (f"Projekt: {project_name}\nEingabe: {user_input}\n"
              f"Kontext: {context_summary[:500]}\n\nWelche 3 Fragen für besseren Prompt?")
    return chat([{"role": "user", "content": prompt}], system=system, temperature=0.5)
