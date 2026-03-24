from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from datetime import datetime
from models import ProjectContext, PromptRequest, FeedbackRequest, ContextUpdate, ChatRequest
from context_store import init_db, get_context, upsert_context, save_feedback, get_all_projects
from prompt_engine import build_optimized_prompt, get_prompt_quality_stats
from chutes_client import generate_questions
from learner import init_learner_db, get_recent_learnings, run_full_learning_cycle

app = FastAPI(title="KORE Agent", description="Context-Orchestration-Research-Engine", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
def startup():
    init_db()
    init_learner_db()
    print("✅ KORE Agent gestartet")

@app.get("/")
def root():
    return {"name": "KORE Agent", "version": "1.0.0", "status": "running"}

@app.get("/projects")
def list_projects():
    return get_all_projects()

@app.get("/context/{project_name}")
def read_context(project_name: str):
    ctx = get_context(project_name)
    if not ctx:
        raise HTTPException(status_code=404, detail=f"Projekt '{project_name}' nicht gefunden")
    return ctx

@app.post("/context/{project_name}")
def write_context(project_name: str, ctx: ProjectContext):
    ctx.project_name = project_name
    upsert_context(ctx)
    return {"status": "ok", "project_name": project_name}

@app.patch("/context/{project_name}")
def patch_context(project_name: str, update: ContextUpdate):
    ctx_data = get_context(project_name)
    if not ctx_data:
        raise HTTPException(status_code=404, detail=f"Projekt '{project_name}' nicht gefunden")
    ctx_data[update.field] = update.value
    upsert_context(ProjectContext(**ctx_data))
    return {"status": "ok", "field": update.field}

@app.post("/prompt")
def generate_prompt(req: PromptRequest):
    if not get_context(req.project_name):
        raise HTTPException(status_code=404, detail=f"Projekt '{req.project_name}' nicht gefunden")
    return build_optimized_prompt(req.project_name, req.user_input, req.user_role)

@app.post("/feedback")
def submit_feedback(fb: FeedbackRequest):
    if fb.quality < 1 or fb.quality > 5:
        raise HTTPException(status_code=400, detail="Quality muss zwischen 1 und 5 sein")
    save_feedback(fb.prompt_id, fb.quality, fb.notes or "")
    return {"status": "ok", "prompt_id": fb.prompt_id}

@app.get("/stats/{project_name}")
def project_stats(project_name: str):
    return get_prompt_quality_stats(project_name)

@app.post("/questions")
def get_clarifying_questions(req: PromptRequest):
    ctx = get_context(req.project_name)
    if not ctx:
        raise HTTPException(status_code=404, detail=f"Projekt '{req.project_name}' nicht gefunden")
    context_summary = ctx.get("system_context", "") + " " + ctx.get("task_context", "")
    questions = generate_questions(req.project_name, req.user_input, context_summary)
    return {"project_name": req.project_name, "questions": questions}

@app.get("/learnings")
def recent_learnings(limit: int = 10):
    return get_recent_learnings(limit)

@app.post("/learn")
def trigger_learning():
    import threading
    threading.Thread(target=run_full_learning_cycle, daemon=True).start()
    return {"status": "Lernzyklus gestartet"}

@app.get("/widget", response_class=HTMLResponse)
def workspace_widget():
    projects = get_all_projects()
    rows = ""
    for p in projects:
        stats = get_prompt_quality_stats(p["project_name"])
        rows += f"<tr><td><strong>{p['project_name']}</strong></td><td>{stats['total_prompts']}</td><td>{stats['avg_quality'] or '—'}</td><td style='color:#888;font-size:12px'>{(p['updated_at'] or '')[:10]}</td></tr>"
    return f"""<!DOCTYPE html><html lang="de"><head><meta charset="UTF-8">
<style>body{{font-family:system-ui,sans-serif;margin:0;padding:16px;background:#f9f9f9;color:#222}}
h2{{font-size:16px;margin:0 0 12px}}table{{width:100%;border-collapse:collapse;font-size:13px}}
th{{text-align:left;padding:6px 8px;border-bottom:2px solid #e0e0e0;color:#666;font-weight:600}}
td{{padding:6px 8px;border-bottom:1px solid #eee}}.badge{{background:#e8f5e9;color:#2e7d32;padding:2px 8px;border-radius:10px;font-size:11px}}
.footer{{margin-top:12px;font-size:11px;color:#aaa}}</style></head><body>
<h2>🧠 KORE Agent <span class="badge">live</span></h2>
<table><thead><tr><th>Projekt</th><th>Prompts</th><th>Ø Qualität</th><th>Aktualisiert</th></tr></thead>
<tbody>{rows}</tbody></table>
<div class="footer">KORE v1.0 · {datetime.now().strftime('%d.%m.%Y %H:%M')} ·
<a href="/learnings" style="color:#aaa">Learnings</a> ·
<a href="/docs" style="color:#aaa">API Docs</a></div>
</body></html>"""

from fastapi.responses import HTMLResponse
import os


from pydantic import BaseModel as BM
class ChatRequest(BM):
    project_name: str
    user_input: str
    user_role: str = 'thomas'
    history: list = []

@app.post('/chat')
def chat_endpoint(req: ChatRequest):
    from chutes_client import chat as chutes_chat
    result = build_optimized_prompt(req.project_name, req.user_input, req.user_role)
    messages = []
    for msg in req.history[-6:]:
        messages.append({'role': msg.get('role','user'), 'content': msg.get('content','')})
    messages.append({'role': 'user', 'content': result['optimized_prompt']})
    system = 'Du bist ein hilfreicher KI-Assistent fuer Paradieschen. Antworte praezise auf Deutsch.'
    answer = chutes_chat(messages, system=system, temperature=0.3, max_tokens=1500)
    return {'answer': answer, 'prompt_id': result['prompt_id'], 'context_used': result['context_used'], 'model': 'Qwen3-235B'}

@app.get("/kore-tab", response_class=HTMLResponse)
def kore_tab():
    tab_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kore-tab.html")
    if os.path.exists(tab_path):
        with open(tab_path, "r", encoding="utf-8") as f:
            return f.read()
    return HTMLResponse("<h2>kore-tab.html nicht gefunden</h2>", status_code=404)

from pydantic import BaseModel as BM
class ChatRequest(BM):
    project_name: str
    user_input: str
    user_role: str = 'thomas'
    history: list = []

@app.post('/chat')
def chat_via_chutes(req: ChatRequest):
    from chutes_client import chat as chutes_chat
    result = build_optimized_prompt(req.project_name, req.user_input, req.user_role)
    messages = []
    for msg in req.history[-6:]:
        messages.append({'role': msg.get('role','user'), 'content': msg.get('content','')})
    messages.append({'role': 'user', 'content': result['optimized_prompt']})
    system = 'Du bist ein hilfreicher KI-Assistent fuer Paradieschen. Antworte auf Deutsch.'
    answer = chutes_chat(messages, system=system, temperature=0.3, max_tokens=1500)
    return {'answer': answer, 'prompt_id': result['prompt_id'], 'context_used': result['context_used'], 'model': 'Qwen3-235B'}
