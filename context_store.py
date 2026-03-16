import sqlite3
from datetime import datetime
from typing import Optional, Dict
from models import ProjectContext

DB_PATH = "kore.db"

PROJECTS_DEFAULT = {
    "paradieschen": {
        "system_context": "Du bist Architekt für Paradieschen, einen Bioladen in Linsengericht (An der Wann 1, 63589). Eigentümer: Kurt Lorenz + Mario Blandamura.",
        "task_context": "Paradieschen nutzt: Kistengenerator (Port 8080/8001 Hetzner), biotaste-v3 (Expo/React Native, Supabase raqvtzzzvhvhyfwyqokm), biotaste-admin (Port 3002), Paradieschen AI Workspace (Port 8090).",
        "knowledge_context": "Kistengenerator: FastAPI+React, live auf Hetzner 89.167.83.224. biotaste: Mitarbeiter-Produktbewertung mit wöchentlicher Verlosung. Admin: PIN-System bcrypt. GitHub: thomassiepmann.",
        "interaction_context": "Antworte auf Deutsch. Code direkt liefern. Thomas ist kein Programmierer — Claude VS Code Extension baut den Code.",
        "situation_context": "Lukas ist IT bei Paradieschen. Bugs: Dashboard hardcoded localhost URLs, KistenFestpreis ignoriert, Root-Passwort im Klartext im Repo — dringend beheben!"
    },
    "meeratmen": {
        "system_context": "Du bist Architekt für MeerAtmen, eine Atemtechnik-App für Konstantin (holisticbreathwork.de).",
        "task_context": "Next.js + Supabase PWA auf Vercel. MVP: Onboarding mit BOLT-Test, Video-Bibliothek (Buteyko, Holistic Breath, Kälte), 7-Tage-Plan, Buchungs-Links.",
        "knowledge_context": "Marken: holisticbreathwork.de (Workshops 80€), meeratmenretreat.de (Retreat Teneriffa 1850-2800€), spiritofice.de (Eisbecken). Monetarisierung: Freemium, Premium 9.99€/Mo.",
        "interaction_context": "Antworte auf Deutsch. Code direkt liefern. Kein React Native für MVP — Web-First.",
        "situation_context": "Video-Hosting: Cloudinary oder Vimeo unlisted. Kein App Store für MVP. Später Capacitor.js."
    },
    "tafill": {
        "system_context": "Du bist Architekt für die Website von Tafill Baumpflege (Konstantin Tafill).",
        "task_context": "Statisches HTML auf Hetzner Port 3000. Domain: tafill-baumpflege.de.",
        "knowledge_context": "Kontakt: 06043-986676, info@baumpflege-tafill.de. Am Sonnenhang 28, 63667 Nidda. European Tree Worker, SKT-A, SKT-B. Farben: #7DC656, #1E3A0F.",
        "interaction_context": "Antworte auf Deutsch. Statisches HTML — kein Framework.",
        "situation_context": "Preview live 89.167.83.224:3000. TODOs: DNS umhängen, SSL, Impressum, echte Fotos."
    },
    "arbos": {
        "system_context": "Du bist Architekt für Arbos, ein autonomes Agenten-Framework auf Bittensor/TAO (geklont von unconst/Arbos, Jacob Stevens).",
        "task_context": "Ziele: Trading via Numinous SN6 + Hyperliquid, Mining MetaNova SN68, Integration SWE-Forge/Proliferate/Boltzmann.",
        "knowledge_context": "Server: Targon Pod SSH rentals-cwgqpzptji9bxvpj@ssh.deployments.targon.com. Code ~/Arbos/. Chutes API Kimi-K2.5 + OpenRouter. Telegram Bot. GitHub: thomassiepmann/arbos-trading.",
        "interaction_context": "Antworte auf Deutsch. Python-Code liefern.",
        "situation_context": "Handshake58 drain-mcp als zukünftige Erweiterung. Tide-Chart Synth SN50 + gTrade geplant."
    },
    "workspace": {
        "system_context": "Du bist Architekt für den Paradieschen AI Workspace, internes Dashboard für Kurt, Lukas und Thomas.",
        "task_context": "Statisches HTML Port 8090 (Nginx, Basic Auth). GitHub: thomassiepmann/biotools-workspace. KI-Chat: DeepSeek-V3 via Chutes + Claude API.",
        "knowledge_context": "Tabs: Übersicht, Möglichkeiten, Briefings, Architektur, Logs, To-Do, KORE (neu). Nutzer: Kurt (Eigentümer), Lukas (IT), Thomas (Builder).",
        "interaction_context": "Antworte auf Deutsch. Statisches HTML — kein Framework.",
        "situation_context": "PC-Gärtner API fehlt (blockiert durch Lukas). KORE wird als neuer Tab eingebaut."
    }
}

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS project_contexts (
        project_name TEXT PRIMARY KEY,
        system_context TEXT DEFAULT '',
        task_context TEXT DEFAULT '',
        knowledge_context TEXT DEFAULT '',
        interaction_context TEXT DEFAULT '',
        situation_context TEXT DEFAULT '',
        updated_at TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS prompt_log (
        id TEXT PRIMARY KEY,
        project_name TEXT,
        user_input TEXT,
        optimized_prompt TEXT,
        user_role TEXT,
        quality INTEGER DEFAULT 0,
        notes TEXT DEFAULT '',
        created_at TEXT)""")
    conn.commit()
    for project, ctx in PROJECTS_DEFAULT.items():
        c.execute("SELECT project_name FROM project_contexts WHERE project_name = ?", (project,))
        if not c.fetchone():
            c.execute("""INSERT INTO project_contexts
                (project_name, system_context, task_context, knowledge_context, interaction_context, situation_context, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (project, ctx["system_context"], ctx["task_context"], ctx["knowledge_context"],
                 ctx["interaction_context"], ctx["situation_context"], datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_context(project_name: str) -> Optional[Dict]:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM project_contexts WHERE project_name = ?", (project_name,))
    row = c.fetchone()
    conn.close()
    if not row:
        return None
    return {"project_name": row[0], "system_context": row[1], "task_context": row[2],
            "knowledge_context": row[3], "interaction_context": row[4],
            "situation_context": row[5], "updated_at": row[6]}

def upsert_context(ctx: ProjectContext):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""INSERT INTO project_contexts
        (project_name, system_context, task_context, knowledge_context, interaction_context, situation_context, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(project_name) DO UPDATE SET
            system_context=excluded.system_context, task_context=excluded.task_context,
            knowledge_context=excluded.knowledge_context, interaction_context=excluded.interaction_context,
            situation_context=excluded.situation_context, updated_at=excluded.updated_at""",
        (ctx.project_name, ctx.system_context, ctx.task_context, ctx.knowledge_context,
         ctx.interaction_context, ctx.situation_context, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def save_prompt_log(prompt_id: str, project_name: str, user_input: str, optimized_prompt: str, user_role: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""INSERT INTO prompt_log (id, project_name, user_input, optimized_prompt, user_role, created_at)
        VALUES (?, ?, ?, ?, ?, ?)""",
        (prompt_id, project_name, user_input, optimized_prompt, user_role, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def save_feedback(prompt_id: str, quality: int, notes: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE prompt_log SET quality = ?, notes = ? WHERE id = ?", (quality, notes, prompt_id))
    conn.commit()
    conn.close()

def get_all_projects() -> list:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT project_name, updated_at FROM project_contexts ORDER BY project_name")
    rows = c.fetchall()
    conn.close()
    return [{"project_name": r[0], "updated_at": r[1]} for r in rows]

def get_top_prompts(project_name: str, limit: int = 5) -> list:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""SELECT user_input, optimized_prompt, quality, created_at FROM prompt_log
        WHERE project_name = ? AND quality >= 4 ORDER BY quality DESC, created_at DESC LIMIT ?""",
        (project_name, limit))
    rows = c.fetchall()
    conn.close()
    return [{"user_input": r[0], "optimized_prompt": r[1], "quality": r[2], "created_at": r[3]} for r in rows]
