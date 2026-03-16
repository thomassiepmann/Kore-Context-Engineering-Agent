import arxiv
import httpx
import sqlite3
import re
from datetime import datetime
from context_store import DB_PATH
from chutes_client import summarize, improve_prompt_template

ARXIV_QUERIES = [
    "context engineering LLM agents",
    "prompt optimization reinforcement learning",
    "retrieval augmented generation context window",
    "autonomous AI agents memory management",
]

DOCS_SOURCES = [
    {"name": "LangChain Concepts", "url": "https://python.langchain.com/docs/concepts/", "topic": "LangChain Context Engineering"},
    {"name": "Anthropic Prompt Engineering", "url": "https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview", "topic": "Anthropic Prompt Engineering"},
]

def init_learner_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS learnings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_type TEXT, source_name TEXT, source_url TEXT,
        summary TEXT, raw_excerpt TEXT, topic TEXT, created_at TEXT)""")
    conn.commit()
    conn.close()

def save_learning(source_type, source_name, source_url, summary, raw_excerpt, topic):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""INSERT INTO learnings (source_type, source_name, source_url, summary, raw_excerpt, topic, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (source_type, source_name, source_url, summary, raw_excerpt, topic, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def fetch_arxiv_papers(max_per_query: int = 2) -> list:
    papers = []
    client = arxiv.Client()
    for query in ARXIV_QUERIES:
        try:
            search = arxiv.Search(query=query, max_results=max_per_query, sort_by=arxiv.SortCriterion.SubmittedDate)
            for paper in client.results(search):
                papers.append({"title": paper.title, "abstract": paper.summary,
                    "url": paper.entry_id, "query": query})
            print(f"  ArXiv '{query}': ok")
        except Exception as e:
            print(f"  ArXiv Fehler: {e}")
    return papers

def fetch_docs(url: str) -> str:
    try:
        r = httpx.get(url, timeout=15.0, follow_redirects=True, headers={"User-Agent": "KORE-Agent/1.0"})
        r.raise_for_status()
        text = re.sub(r'<[^>]+>', ' ', r.text)
        return re.sub(r'\s+', ' ', text).strip()[:3000]
    except Exception as e:
        return f"[FETCH FEHLER] {e}"

def learn_from_arxiv():
    print("\n📚 ArXiv Paper laden...")
    for paper in fetch_arxiv_papers():
        text = f"Titel: {paper['title']}\n\nAbstract: {paper['abstract']}"
        summary = summarize(text, topic=paper["query"])
        save_learning("arxiv", paper["title"], paper["url"], summary, paper["abstract"][:500], paper["query"])
        print(f"  ✅ {paper['title'][:60]}...")

def learn_from_docs():
    print("\n📖 Docs lesen...")
    for source in DOCS_SOURCES:
        content = fetch_docs(source["url"])
        if content.startswith("[FETCH FEHLER]"):
            print(f"  ⚠️  {content}")
            continue
        summary = summarize(content, topic=source["topic"])
        save_learning("docs", source["name"], source["url"], summary, content[:500], source["topic"])
        print(f"  ✅ {source['name']}")

def run_rl_improvement():
    from context_store import get_context, upsert_context
    from models import ProjectContext
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""SELECT project_name, optimized_prompt, quality, notes FROM prompt_log
        WHERE quality > 0 AND quality <= 2 AND created_at > datetime('now', '-7 days')""")
    bad = c.fetchall()
    conn.close()
    if not bad:
        print("\n🤖 RL: Keine schlechten Prompts diese Woche.")
        return
    by_project = {}
    for row in bad:
        by_project.setdefault(row[0], []).append({"prompt": row[1][:300], "quality": row[2], "notes": row[3]})
    for project_name, examples in by_project.items():
        ctx = get_context(project_name)
        if not ctx:
            continue
        improved = improve_prompt_template(ctx["interaction_context"], examples)
        ctx["interaction_context"] = improved
        upsert_context(ProjectContext(**ctx))
        print(f"  ✅ RL Verbesserung: {project_name}")

def get_recent_learnings(limit: int = 10) -> list:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""SELECT source_type, source_name, summary, topic, created_at
        FROM learnings ORDER BY created_at DESC LIMIT ?""", (limit,))
    rows = c.fetchall()
    conn.close()
    return [{"source_type": r[0], "source_name": r[1], "summary": r[2],
             "topic": r[3], "created_at": r[4]} for r in rows]

def run_full_learning_cycle():
    print(f"\n🧠 KORE Learner: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    init_learner_db()
    learn_from_arxiv()
    learn_from_docs()
    run_rl_improvement()
    print(f"\n✅ Fertig: {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    run_full_learning_cycle()
