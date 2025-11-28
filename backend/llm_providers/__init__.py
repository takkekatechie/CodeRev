"""
LLM Providers package for CodeReviewPro
Supports multiple LLM providers for code analysis
"""

from .base_provider import BaseLLMProvider
from .openai_provider import OpenAIProvider
from .gemini_provider import GeminiProvider
from .anthropic_provider import AnthropicProvider
from .perplexity_provider import PerplexityProvider
from .openrouter_provider import OpenRouterProvider

__all__ = [
    'BaseLLMProvider',
    'OpenAIProvider',
    'GeminiProvider',
    'AnthropicProvider',
    'PerplexityProvider',
    'OpenRouterProvider',
]


def get_provider(provider_name: str, config: dict):
    """Factory function to get the appropriate LLM provider"""
    providers = {
        'openai': OpenAIProvider,
        'gemini': GeminiProvider,
        'anthropic': AnthropicProvider,
        'perplexity': PerplexityProvider,
        'openrouter': OpenRouterProvider,
    }
    
    provider_class = providers.get(provider_name.lower())
    if not provider_class:
        raise ValueError(f"Unknown provider: {provider_name}")
    
    return provider_class(config)
