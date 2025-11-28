"""
Base LLM Provider interface
All LLM providers must implement this interface
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import time
from collections import deque


class BaseLLMProvider(ABC):
    """Abstract base class for all LLM providers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_key = config.get('api_key', '')
        self.model = config.get('model', '')
        self.max_tokens = config.get('max_tokens', 2000)
        self.temperature = config.get('temperature', 0.3)
        
        # Rate limiting
        self.rate_limit_config = config.get('rate_limit', {})
        self.requests_per_minute = self.rate_limit_config.get('requests_per_minute', 10)
        self.requests_per_hour = self.rate_limit_config.get('requests_per_hour', 100)
        
        # Track request timestamps for rate limiting
        self.request_timestamps = deque(maxlen=self.requests_per_hour)
    
    @abstractmethod
    def check_availability(self) -> bool:
        """
        Check if the provider is available and properly configured
        Returns True if API key is valid and service is accessible
        """
        pass
    
    @abstractmethod
    def check_credits(self) -> bool:
        """
        Check if there are sufficient credits/quota available
        Returns True if credits are available, False otherwise
        """
        pass
    
    @abstractmethod
    def analyze_code(self, file_path: str, content: str, language: str) -> List[Dict[str, Any]]:
        """
        Analyze code using the LLM
        
        Args:
            file_path: Path to the file being analyzed
            content: Content of the file
            language: Programming language of the file
        
        Returns:
            List of issues found in the format:
            [
                {
                    'category': 'security|bug|performance|maintainability',
                    'severity': 'error|warning|info',
                    'line_start': int,
                    'line_end': int,
                    'description': str,
                    'recommendation': str
                }
            ]
        """
        pass
    
    def check_rate_limit(self) -> bool:
        """Check if we're within rate limits"""
        now = time.time()
        
        # Remove timestamps older than 1 hour
        while self.request_timestamps and now - self.request_timestamps[0] > 3600:
            self.request_timestamps.popleft()
        
        # Check hourly limit
        if len(self.request_timestamps) >= self.requests_per_hour:
            return False
        
        # Check per-minute limit
        recent_requests = sum(1 for ts in self.request_timestamps if now - ts < 60)
        if recent_requests >= self.requests_per_minute:
            return False
        
        return True
    
    def record_request(self):
        """Record a new request for rate limiting"""
        self.request_timestamps.append(time.time())
    
    def build_analysis_prompt(self, file_path: str, content: str, language: str) -> str:
        """Build a prompt for code analysis"""
        prompt = f"""You are an expert code reviewer. Analyze the following {language} code and identify issues.

File: {file_path}

Code:
```{language}
{content}
```

Please identify issues in the following categories:
1. Security vulnerabilities (SQL injection, XSS, hardcoded secrets, etc.)
2. Bugs and logic errors
3. Performance issues
4. Maintainability and code quality issues

For each issue, provide:
- Category (security, bug, performance, or maintainability)
- Severity (error, warning, or info)
- Line number(s) where the issue occurs
- Clear description of the issue
- Recommendation for fixing it

Format your response as a JSON array of issues:
[
  {{
    "category": "security",
    "severity": "error",
    "line_start": 10,
    "line_end": 10,
    "description": "Hardcoded API key detected",
    "recommendation": "Move API key to environment variables"
  }}
]

If no issues are found, return an empty array: []
"""
        return prompt
    
    def parse_llm_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse LLM response and extract issues"""
        import json
        import re
        
        try:
            # Try to find JSON array in the response
            json_match = re.search(r'\[[\s\S]*\]', response)
            if json_match:
                issues = json.loads(json_match.group())
                return issues if isinstance(issues, list) else []
            
            # If no JSON found, try parsing the entire response
            issues = json.loads(response)
            return issues if isinstance(issues, list) else []
            
        except json.JSONDecodeError:
            # If parsing fails, return empty list
            return []
    
    def validate_api_key(self) -> bool:
        """Check if API key is configured"""
        return bool(self.api_key and self.api_key.strip())
