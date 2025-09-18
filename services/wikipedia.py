from typing import List, Dict, Any
import requests

UA = {"User-Agent": "AI-Podcast-Assistant/1.0 (educational use)"}

def search(query: str, top_n: int = 3, lang: str = "en") -> List[Dict[str, Any]]:
    """
    Wikipedia official API; no key needed.
    Returns list of {title, url, summary}.
    """
    query = (query or "").strip()
    if not query:
        return []
    endpoint = f"https://{lang}.wikipedia.org/w/api.php"

    try:
        s = requests.get(
            endpoint,
            params={
                "action": "query",
                "list": "search",
                "srsearch": query[:256],  # bound length
                "format": "json",
                "srlimit": max(0, min(top_n, 10)),
                "utf8": 1
            },
            headers=UA, timeout=15
        ).json()
        results = []
        for item in s.get("query", {}).get("search", []):
            pageid = item.get("pageid")
            title = item.get("title")
            e = requests.get(
                endpoint,
                params={
                    "action": "query",
                    "prop": "extracts",
                    "exintro": 1,
                    "explaintext": 1,
                    "pageids": pageid,
                    "format": "json",
                    "utf8": 1
                },
                headers=UA, timeout=15
            ).json()
            extract = ""
            pages = e.get("query", {}).get("pages", {})
            if str(pageid) in pages:
                extract = pages[str(pageid)].get("extract", "") or ""
            url = f"https://{lang}.wikipedia.org/?curid={pageid}"
            results.append({"source": "Wikipedia", "title": title, "url": url, "summary": extract})
        return results
    except Exception:
        return []
