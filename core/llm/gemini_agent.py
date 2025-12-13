import logging
from typing import Any, Optional
from google import genai
from google.genai import types

from .base import BaseAgent
from .types import LLMResponse

logger = logging.getLogger(__name__)

class GeminiAgent(BaseAgent):
    def __init__(self, model: str = "gemini-2.5-flash", api_key: Optional[str] = None, **kwargs):
        self.client = genai.Client(api_key=api_key) if api_key else genai.Client()
        self._model = model
        self.config = kwargs

    def model_name(self) -> str:
        return self._model

    def generate(
        self, 
        prompt: str, 
        tools: Optional[list] = None, 
        response_schema: Optional[Any] = None, 
        json_mode: bool = False,
        timeout: Optional[float] = 30.0
    ) -> LLMResponse:
        config = types.GenerateContentConfig(
            tools=tools,
            response_mime_type="application/json" if json_mode or response_schema else None,
            response_schema=response_schema,
        )

        try:
            resp = self.client.models.generate_content(
                model=self._model,
                contents=prompt,
                config=config
            )

            text = getattr(resp, "text", "") or ""
            meta = {}
            if hasattr(resp, "usage_metadata"):
                meta["usage"] = {
                    "prompt_token_count": resp.usage_metadata.prompt_token_count,
                    "candidates_token_count": resp.usage_metadata.candidates_token_count,
                    "total_token_count": resp.usage_metadata.total_token_count
                }

            return LLMResponse(
                text=text,
                raw=resp,
                provider="google",
                model=self._model,
                meta=meta
            )

        except Exception as e:
            logger.error(f"Gemini error: {e}")
            raise

    def generate_stream(self, prompt: str, tools: Optional[list] = None, **kwargs):
        config = types.GenerateContentConfig(
            tools=tools
        )
        try:
            stream = self.client.models.generate_content_stream(
                model=self._model,
                contents=prompt,
                config=config
            )
            for chunk in stream:
                 if chunk.text:
                     yield chunk.text
        except Exception as e:
             logger.error(f"Gemini stream error: {e}")
             yield f"[Error: {str(e)}]"
