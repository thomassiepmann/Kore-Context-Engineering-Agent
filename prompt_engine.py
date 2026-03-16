import uuid
from context_store import get_context, save_prompt_log, get_top_prompts

USER_ROLES = {
    "thomas": "Du bist Thomas, Projektkoordinator und Builder. Kein Programmierer. Arbeitest mit Claude als VS Code Extension.",
    "kurt": "Du bist Kurt, Eigentümer von Paradieschen. Kein Tech-Hintergrund. Brauchst klare einfache Antworten auf Deutsch.",
    "lukas": "Du bist Lukas, IT-Ansprechpartner bei Paradieschen. Tech-affin, kennt Server und Infrastruktur."
}

def build_optimized_prompt(project_name: str, user_input: str, user_role: str = "thomas") -> dict:
    ctx = get_context(project_name)
    context_used = []
    prompt_parts = []

    role_desc = USER_ROLES.get(user_role, USER_ROLES["thomas"])
    prompt_parts.append(f"[NUTZER-KONTEXT]\n{role_desc}")
    context_used.append("user_role")

    if ctx:
        if ctx["system_context"]:
            prompt_parts.append(f"[SYSTEM-KONTEXT]\n{ctx['system_context']}")
            context_used.append("system_context")
        if ctx["task_context"]:
            prompt_parts.append(f"[AUFGABEN-KONTEXT]\n{ctx['task_context']}")
            context_used.append("task_context")
        if ctx["knowledge_context"]:
            prompt_parts.append(f"[WISSENS-KONTEXT]\n{ctx['knowledge_context']}")
            context_used.append("knowledge_context")
        if ctx["situation_context"]:
            prompt_parts.append(f"[SITUATIONS-KONTEXT]\n{ctx['situation_context']}")
            context_used.append("situation_context")
        if ctx["interaction_context"]:
            prompt_parts.append(f"[INTERAKTIONS-KONTEXT]\n{ctx['interaction_context']}")
            context_used.append("interaction_context")

    top_prompts = get_top_prompts(project_name, limit=2)
    if top_prompts:
        examples = "\n".join([f"- Eingabe: {p['user_input'][:80]}..." for p in top_prompts])
        prompt_parts.append(f"[BEWÄHRTE ANFRAGEN]\n{examples}")
        context_used.append("learned_prompts")

    prompt_parts.append(f"[ANFRAGE]\n{user_input}")
    optimized = "\n\n".join(prompt_parts)
    prompt_id = str(uuid.uuid4())[:8]
    save_prompt_log(prompt_id, project_name, user_input, optimized, user_role)
    return {"prompt_id": prompt_id, "optimized_prompt": optimized,
            "project_name": project_name, "context_used": context_used}

def get_prompt_quality_stats(project_name: str) -> dict:
    import sqlite3
    from context_store import DB_PATH
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""SELECT COUNT(*), AVG(CASE WHEN quality > 0 THEN quality END),
        COUNT(CASE WHEN quality >= 4 THEN 1 END)
        FROM prompt_log WHERE project_name = ?""", (project_name,))
    row = c.fetchone()
    conn.close()
    return {"total_prompts": row[0] or 0,
            "avg_quality": round(row[1], 2) if row[1] else 0,
            "good_prompts": row[2] or 0}
