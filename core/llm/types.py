from dataclasses import dataclass
from typing import Any, Optional, Dict

@dataclass
class LLMResponse:
    text: str                   # clean text
    raw: Any                    # raw provider response object
    provider: str               # e.g. "openai" | "google" | "anthropic"
    model: str                  # model name
    meta: Optional[Dict] = None # token usage, latency...
