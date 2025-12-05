import json
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

def safe_json_parse(text: str) -> Dict[str, Any]:
    text = text.strip()

    # strip codeblock
    if text.startswith("```"):
        first_nl = text.find("\n")
        if first_nl != -1:
            # Check if it's json block
            if text[:first_nl].strip().lower().endswith("json"):
                text = text[first_nl+1:]
            else:
                text = text[3:]
        
        # Find the last ```
        last_backtick = text.rfind("```")
        if last_backtick != -1:
            text = text[:last_backtick]

    try:
        return json.loads(text.strip())
    except Exception:
        logger.warning(f"JSON parse failed for text: {text[:100]}...", exc_info=True)
        return {}
