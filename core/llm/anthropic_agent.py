import logging
from typing import Any, Optional
from anthropic import Anthropic

from .base import BaseAgent
from .types import LLMResponse

logger = logging.getLogger(__name__)

class AnthropicAgent(BaseAgent):
    def __init__(self, model: str = "claude-3-5-sonnet-20241022", api_key: Optional[str] = None, **kwargs):
        
        self.client = Anthropic(api_key=api_key)
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
            response = self.client.messages.create(
                model=self._model,
                messages=[{"role": "user", "content": prompt}],
                tools=tools,
                max_tokens=4096,
                timeout=timeout
            )

            # Anthropic trả về content dạng list
            text = ""
            if response.content and len(response.content):
                block = response.content[0]
                if block.type == "text":
                    text = block.text

            meta = {
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                }
            }

            return LLMResponse(
                text=text,
                raw=response,
                provider="anthropic",
                model=self._model,
                meta=meta
            )

        except Exception as e:
            logger.error(f"Anthropic error: {e}")
            raise
