from dataclasses import dataclass
from functools import lru_cache
import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

@dataclass(frozen=True)
class Settings:
    llm_provider: str | None
    llm_model: str | None
    hf_api_token: str | None

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings(
        llm_provider=(os.getenv("LLM_PROVIDER") or "none").lower(),
        llm_model=os.getenv("LLM_MODEL") or "meta-llama/Meta-Llama-3-8B-Instruct",
        hf_api_token=os.getenv("HUGGINGFACE_API_TOKEN") or None,
    )
