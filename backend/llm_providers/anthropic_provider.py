"""
Anthropic Claude Provider
"""

from typing import List, Dict, Any
from .base_provider import BaseLLMProvider


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude provider for code analysis"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Anthropic client"""
        try:
            import anthropic
            if self.validate_api_key():
                self.client = anthropic.Anthropic(api_key=self.api_key)
        except ImportError:
            pass
    
    def check_availability(self) -> bool:
        """Check if Anthropic is available"""
        if not self.validate_api_key():
            return False
        
        if not self.client:
            return False
        
        try:
            # Try a simple API call to verify the key
            self.client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Hi"}]
            )
            return True
        except Exception:
            return False
    
    def check_credits(self) -> bool:
        """Check if credits are available"""
        return self.check_rate_limit()
    
    def analyze_code(self, file_path: str, content: str, language: str) -> List[Dict[str, Any]]:
        """Analyze code using Claude"""
        if not self.client:
            return []
        
        if not self.check_rate_limit():
            return []
        
        try:
            prompt = self.build_analysis_prompt(file_path, content, language)
            
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            self.record_request()
            
            # Parse response
            if message.content and len(message.content) > 0:
                response_text = message.content[0].text
                return self.parse_llm_response(response_text)
            
            return []
            
        except Exception as e:
            import logging
            logging.error(f"Anthropic analysis error: {e}")
            return []
