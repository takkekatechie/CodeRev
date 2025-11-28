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
            List of issues found
        """
        pass
    
    def analyze_code_batch(self, files: List[Dict[str, str]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Analyze multiple files in one API call (batch processing)
        No timeout limit - will wait for LLM to complete
        
        Args:
            files: List of dicts with 'path', 'content', 'language' keys
        
        Returns:
            Dict mapping file paths to their issues
        """
        # Default implementation: call analyze_code for each file
        # Providers can override for true batch processing
        results = {}
        for file_info in files:
            try:
                issues = self.analyze_code(
                    file_info['path'],
                    file_info['content'],
                    file_info['language']
                )
                results[file_info['path']] = issues
            except Exception:
                results[file_info['path']] = []
        
        return results
    
    def build_batch_prompt(self, files: List[Dict[str, str]]) -> str:
        """Build optimized prompt for analyzing multiple files"""
        prompt = "You are an expert code reviewer. Analyze the following code files and identify issues in each.\n\nFiles to analyze:\n"
        
        for i, file_info in enumerate(files, 1):
            prompt += f"\n--- File {i}: {file_info['path']} ({file_info['language']}) ---\n"
            prompt += f"```{file_info['language']}\n{file_info['content']}\n```\n"
        
        prompt += """
For EACH file, identify issues in these categories:
1. Security vulnerabilities (SQL injection, XSS, hardcoded secrets, etc.)
2. Bugs and logic errors
3. Performance issues
4. Maintainability and code quality issues

Format your response as a JSON object where keys are file paths and values are arrays of issues:
{
  "file1.py": [
    {
      "category": "security",
      "severity": "error",
      "line_start": 10,
      "line_end": 10,
      "description": "Hardcoded API key detected",
      "recommendation": "Move API key to environment variables"
    }
  ],
  "file2.js": []
}

If a file has no issues, use an empty array.
"""
        return prompt
    
    def parse_batch_response(self, response: str, file_paths: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """Parse batch response and extract per-file issues"""
        import json
        import re
        
        try:
            # Try to find JSON object in the response
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                result = json.loads(json_match.group())
                if isinstance(result, dict):
                    # Ensure all files are in the result
                    for path in file_paths:
                        if path not in result:
                            result[path] = []
                    return result
            
            # If parsing fails, return empty results for all files
            return {path: [] for path in file_paths}
            
        except json.JSONDecodeError:
            return {path: [] for path in file_paths}
    
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
