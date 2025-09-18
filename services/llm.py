# services/llm.py
from typing import Optional
import textwrap
import requests
from config.settings import get_settings

def available() -> bool:
    s = get_settings()
    return s.llm_provider == "huggingface" and bool(s.hf_api_token)

def _trim(text: str, max_chars: int = 6000) -> str:
    return text[:max_chars]

def summarize_with_llm(text: str, topic_hint: Optional[str] = None,
                       max_new_tokens: int = 700, temperature: float = 0.2) -> Optional[str]:
    """
    Uses Hugging Face Inference API for meta-llama/Meta-Llama-3-8B-Instruct.
    Returns summary text or None on failure.
    """
    s = get_settings()
    if s.llm_provider != "huggingface" or not s.hf_api_token:
        return None

    model = s.llm_model or "meta-llama/Meta-Llama-3-8B-Instruct"
    url = f"https://api-inference.huggingface.co/models/{model}"
    headers = {"Authorization": f"Bearer {s.hf_api_token}"}

    prompt = f"""You are a careful assistant. Summarize the following document for a global audience.
- Write a tight executive summary (5–8 bullet points) and a short paragraph.
- If a topic hint is given, emphasize it: {topic_hint or "(none)"}.
- When you use external context (provided separately), cite with tags like [W1], [S2], [O3], [C1].
- If a claim is not supported by provided context, say so.

Document:
{textwrap.shorten(_trim(text), width=5500, placeholder=' ...')}

Return just the summary content, not JSON.
"""
    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": max_new_tokens, "temperature": temperature, "return_full_text": False}
    }

    try:
        r = requests.post(url, headers=headers, json=payload, timeout=90)
        r.raise_for_status()
        data = r.json()
        # HF can return list or dict
        if isinstance(data, list) and data and "generated_text" in data[0]:
            return data[0]["generated_text"].strip()
        if isinstance(data, dict) and "generated_text" in data:
            return data["generated_text"].strip()
        # Some models return a different envelope; fallback:
        return str(data)[:4000]
    except Exception:
        return None
