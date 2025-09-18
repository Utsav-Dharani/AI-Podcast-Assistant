# services/openalex.py
from typing import List, Dict, Any
import requests

UA = {"User-Agent": "AI-Podcast-Assistant/1.0 (educational use)"}

def search_works(query: str, top_n: int = 5) -> List[Dict[str, Any]]:
    """
    OpenAlex: free scholarly metadata (https://api.openalex.org/).
    """
    query = (query or "").strip()
    if not query:
        return []
    url = "https://api.openalex.org/works"
    params = {"search": query[:256], "per_page": max(0, min(top_n, 10))}
    try:
        r = requests.get(url, params=params, headers=UA, timeout=20)
        r.raise_for_status()
        j = r.json()
        out = []
        for w in j.get("results", []):
            title = w.get("title","")
            year  = w.get("publication_year")
            host  = (w.get("host_venue") or {}).get("display_name")
            url_w = w.get("primary_location", {}).get("source", {}).get("url") or w.get("id")
            abs_  = w.get("abstract_inverted_index")
            # reconstruct abstract if available
            if isinstance(abs_, dict):
                inv = abs_
                words = sorted([(pos, token) for token, positions in inv.items() for pos in positions])
                abstract = " ".join(token for _, token in words)
            else:
                abstract = ""
            out.append({
                "source": "OpenAlex",
                "title": title, "year": year, "venue": host,
                "url": url_w, "summary": abstract or "(No abstract)"
            })
        return out
    except Exception:
        return []
