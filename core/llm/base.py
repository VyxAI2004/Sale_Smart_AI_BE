from abc import ABC, abstractmethod
from typing import Any, Optional
from .types import LLMResponse

class BaseAgent(ABC):
    """
    Abstract base class for all LLM agents.
    Enforces type-safe interface for LLM operations.
    """
    
    @abstractmethod
    def generate(
        self, 
        prompt: str, 
        tools: Optional[list] = None, 
        response_schema: Optional[Any] = None,
        json_mode: bool = False,
        timeout: Optional[float] = 30.0
    ) -> LLMResponse:
        """Generate content using LLM"""
        pass

    @abstractmethod
    def model_name(self) -> str:
        """Return the model name"""
        pass
