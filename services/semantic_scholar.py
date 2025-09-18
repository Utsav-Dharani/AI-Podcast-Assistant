from typing import List, Dict, Any
import requests
from config.settings import get_settings

UA = {"User-Agent": "AI-Podcast-Assistant/1.0 (educational use)"}

def search(query: str, top_n: int = 5) -> List[Dict[str, Any]]:
    """
    Semantic Scholar Graph API (trusted alternative to Google Scholar).
    If SEMANTIC_SCHOLAR_API_KEY is set, use it for better limits; otherwise works unauthenticated.
    """
    query = (query or "").strip()
    if not query:
        return []
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": query[:256],
        "limit": max(0, min(top_n, 10)),
        "fields": "title,abstract,year,venue,url,authors"
    }
    headers = dict(UA)
    s = get_settings()
    if s.s2_api_key:
        headers["x-api-key"] = s.s2_api_key

    try:
        r = requests.get(url, params=params, headers=headers, timeout=20)
        r.raise_for_status()
        data = r.json()
        out: List[Dict[str, Any]] = []
        for p in data.get("data", []):
            authors = ", ".join([a.get("name", "") for a in p.get("authors", [])][:5])
            out.append({
                "source": "Semantic Scholar",
                "title": p.get("title", ""),
                "url": p.get("url", ""),
                "summary": p.get("abstract", "") or "(No abstract provided.)",
                "year": p.get("year"),
                "venue": p.get("venue"),
                "authors": authors
            })
        return out
    except Exception:
        return []
