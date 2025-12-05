import logging
from typing import Any, Optional
from openai import OpenAI

from .base import BaseAgent
from .types import LLMResponse

logger = logging.getLogger(__name__)

class OpenAIAgent(BaseAgent):
    def __init__(self, model: str = "gpt-4.1", api_key: Optional[str] = None, **kwargs):
        self.client = OpenAI(api_key=api_key)
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
        timeout: Optional[float] = 30.0,
    ) -> LLMResponse:
        try:
            response = self.client.chat.completions.create(
                model=self._model,
                messages=[{"role": "user", "content": prompt}],
                tools=tools,
                response_format=(
                    {"type": "json_object"} if (json_mode or response_schema) else None
                ),
                timeout=timeout,
            )

            text = response.choices[0].message.content or ""

            meta = {
                "usage": dict(response.usage) if hasattr(response, "usage") else {}
            }

            return LLMResponse(
                text=text,
                raw=response,
                provider="openai",
                model=self._model,
                meta=meta
            )

        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            raise
