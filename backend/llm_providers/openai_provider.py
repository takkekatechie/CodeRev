"""
OpenAI Provider for GPT-4 and GPT-3.5-turbo
"""

from typing import List, Dict, Any
from .base_provider import BaseLLMProvider


class OpenAIProvider(BaseLLMProvider):
    """OpenAI GPT provider for code analysis"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize OpenAI client"""
        try:
            import openai
            if self.validate_api_key():
                self.client = openai.OpenAI(api_key=self.api_key)
        except ImportError:
            pass
    
    def check_availability(self) -> bool:
        """Check if OpenAI is available"""
        if not self.validate_api_key():
            return False
        
        if not self.client:
            return False
        
        try:
            # Try a simple API call to verify the key
            self.client.models.list()
            return True
        except Exception:
            return False
    
    def check_credits(self) -> bool:
        """
        Check if credits are available
        Note: OpenAI doesn't provide a direct API for checking credits,
        so we'll return True and rely on error handling
        """
        return self.check_rate_limit()
    
    def analyze_code(self, file_path: str, content: str, language: str) -> List[Dict[str, Any]]:
        """Analyze code using OpenAI GPT"""
        if not self.client:
            return []
        
        if not self.check_rate_limit():
            return []
        
        try:
            prompt = self.build_analysis_prompt(file_path, content, language)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert code reviewer. Analyze code and return issues in JSON format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                response_format={"type": "json_object"} if "gpt-4" in self.model else None
            )
            
            self.record_request()
            
            # Parse response
            content = response.choices[0].message.content
            
            # Handle JSON object response format
            if "gpt-4" in self.model:
                import json
                try:
                    result = json.loads(content)
                    # Extract issues array from the response
                    if isinstance(result, dict) and 'issues' in result:
                        return result['issues']
                    elif isinstance(result, list):
                        return result
                except json.JSONDecodeError:
                    pass
            
            return self.parse_llm_response(content)
            
        except Exception as e:
            # Log error and return empty list
            import logging
            logging.error(f"OpenAI analysis error: {e}")
            return []
