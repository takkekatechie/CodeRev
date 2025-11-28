"""
Perplexity Provider
"""

from typing import List, Dict, Any
from .base_provider import BaseLLMProvider


class PerplexityProvider(BaseLLMProvider):
    """Perplexity provider for code analysis"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_url = "https://api.perplexity.ai/chat/completions"
    
    def check_availability(self) -> bool:
        """Check if Perplexity is available"""
        if not self.validate_api_key():
            return False
        
        try:
            import httpx
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Simple test request
            response = httpx.post(
                self.api_url,
                headers=headers,
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": "Hi"}],
                    "max_tokens": 10
                },
                timeout=10.0
            )
            
            return response.status_code == 200
        except Exception:
            return False
    
    def check_credits(self) -> bool:
        """Check if credits are available"""
        return self.check_rate_limit()
    
    def analyze_code(self, file_path: str, content: str, language: str) -> List[Dict[str, Any]]:
        """Analyze code using Perplexity"""
        if not self.validate_api_key():
            return []
        
        if not self.check_rate_limit():
            return []
        
        try:
            import httpx
            
            prompt = self.build_analysis_prompt(file_path, content, language)
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert code reviewer. Analyze code and return issues in JSON format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": self.max_tokens,
                "temperature": self.temperature
            }
            
            response = httpx.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30.0
            )
            
            self.record_request()
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    content = result['choices'][0]['message']['content']
                    return self.parse_llm_response(content)
            
            return []
            
        except Exception as e:
            import logging
            logging.error(f"Perplexity analysis error: {e}")
            return []
