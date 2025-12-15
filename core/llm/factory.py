from .gemini_agent import GeminiAgent
from .openai_agent import OpenAIAgent
from .anthropic_agent import AnthropicAgent

class AgentFactory:
    @staticmethod
    def create(provider: str, model: str = None, api_key: str = None, **kwargs):
        provider = provider.lower()

        if provider in ["google", "gemini"]:
            return GeminiAgent(model=model or "gemini-2.5-flash", api_key=api_key, **kwargs)

        if provider == "openai":
            return OpenAIAgent(model=model or "gpt-4.1-mini", api_key=api_key, **kwargs)

        if provider == "anthropic" or provider == "claude":
            return AnthropicAgent(model or "claude-3-sonnet")

        raise ValueError(f"Unsupported provider: {provider}")
