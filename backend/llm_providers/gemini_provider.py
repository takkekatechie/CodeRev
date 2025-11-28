"""
Google Gemini Provider
"""

from typing import List, Dict, Any
from .base_provider import BaseLLMProvider


class GeminiProvider(BaseLLMProvider):
    """Google Gemini provider for code analysis"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Gemini client"""
        try:
            import google.generativeai as genai
            if self.validate_api_key():
                genai.configure(api_key=self.api_key)
                self.client = genai.GenerativeModel(self.model)
        except ImportError:
            pass
    
    def check_availability(self) -> bool:
        """Check if Gemini is available"""
        if not self.validate_api_key():
            return False
        
        if not self.client:
            return False
        
        try:
            # Try a simple generation to verify the key
            response = self.client.generate_content("Hello")
            return bool(response)
        except Exception:
            return False
    
    def check_credits(self) -> bool:
        """Check if credits are available"""
        return self.check_rate_limit()
    
    def analyze_code(self, file_path: str, content: str, language: str) -> List[Dict[str, Any]]:
        """Analyze code using Gemini"""
        if not self.client:
            return []
        
        if not self.check_rate_limit():
            return []
        
        try:
            prompt = self.build_analysis_prompt(file_path, content, language)
            
            # Configure generation
            generation_config = {
                "temperature": self.temperature,
                "max_output_tokens": self.max_tokens,
            }
            
            response = self.client.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            self.record_request()
            
            # Parse response
            if response and response.text:
                return self.parse_llm_response(response.text)
            
            return []
            
        except Exception as e:
            import logging
            logging.error(f"Gemini analysis error: {e}")
            return []
