# services/rag.py
from typing import List, Dict
from services import wikipedia, semantic_scholar as s2, openalex
from services import llm
from utils.text import summarize_text

def gather_context(query: str, k_wiki: int = 3, k_s2: int = 4, k_oa: int = 3) -> Dict[str, List[Dict]]:
    return {
        "wiki": wikipedia.search(query, top_n=k_wiki),
        "s2": s2.search(query, top_n=k_s2),
        "oa": openalex.search_works(query, top_n=k_oa),
    }

def render_context_for_prompt(ctx: Dict[str, List[Dict]]) -> str:
    """
    Returns a compact, tag-labeled context block like:
    [W1] Title — summary...
    [S2] Paper Title — abstract...
    [O3] OpenAlex Title — abstract...
    """
    lines: List[str] = []
    for i, r in enumerate(ctx.get("wiki", []), start=1):
        lines.append(f"[W{i}] {r.get('title')}: {r.get('summary','')[:800]}")
    for i, r in enumerate(ctx.get("s2", []), start=1):
        bits = []
        if r.get("authors"): bits.append(r["authors"])
        if r.get("venue"):   bits.append(r["venue"])
        if r.get("year"):    bits.append(str(r["year"]))
        meta = " • ".join(bits)
        lines.append(f"[S{i}] {r.get('title')} ({meta}): {r.get('summary','')[:900]}")
    for i, r in enumerate(ctx.get("oa", []), start=1):
        bits = []
        if r.get("venue"): bits.append(r["venue"])
        if r.get("year"):  bits.append(str(r["year"]))
        meta = " • ".join(bits)
        lines.append(f"[O{i}] {r.get('title')} ({meta}): {r.get('summary','')[:900]}")
    return "\n".join(lines[:20])  # cap tokens

def summarize_with_context(pdf_text: str, query: str) -> str:
    ctx = gather_context(query)
    ctx_block = render_context_for_prompt(ctx)
    # Try LLM first
    if llm.available():
        prompt_hint = f"{query}".strip() or None
        combined = f"{pdf_text}\n\nExternal Context:\n{ctx_block}"
        out = llm.summarize_with_llm(combined, topic_hint=prompt_hint)
        if out:
            return out
    # Fallback: local extractive summary (no keys)
    base = summarize_text(pdf_text, max_sentences=8)
    return f"{base}\n\n_(LLM unavailable; showing local summary. External context seen but not synthesized.)_"
