"""
JSON analyzer for schema validation and structure analysis
"""

import json
from typing import List, Set
from .base_analyzer import BaseAnalyzer, Issue, IssueCategory, IssueSeverity

class JSONAnalyzer(BaseAnalyzer):
    """Analyzer for JSON files"""
    
    def get_supported_extensions(self) -> List[str]:
        return ['.json']
    
    def analyze_file(self, file_path: str, content: str) -> List[Issue]:
        """Analyze JSON file"""
        issues = []
        
        try:
            # Parse JSON
            data = json.loads(content)
            
            # Check for duplicate keys (requires custom parsing)
            issues.extend(self._check_duplicate_keys(file_path, content))
            
            # Check for large file
            if len(content) > 1024 * 1024:  # 1MB
                issues.append(self.create_issue(
                    IssueCategory.PERFORMANCE,
                    IssueSeverity.WARNING,
                    file_path,
                    1,
                    1,
                    f"Large JSON file ({len(content) // 1024}KB)",
                    "Consider splitting into smaller files or using a more efficient format."
                ))
            
            # Check for deeply nested structures
            max_depth = self._get_max_depth(data)
            if max_depth > 10:
                issues.append(self.create_issue(
                    IssueCategory.MAINTAINABILITY,
                    IssueSeverity.INFO,
                    file_path,
                    1,
                    1,
                    f"Deeply nested JSON structure (depth: {max_depth})",
                    "Consider flattening the structure for better readability and performance."
                ))
            
        except json.JSONDecodeError as e:
            issues.append(self.create_issue(
                IssueCategory.BUG,
                IssueSeverity.ERROR,
                file_path,
                e.lineno,
                e.lineno,
                f"Invalid JSON: {e.msg}",
                "Fix the JSON syntax error."
            ))
        
        return issues
    
    def _check_duplicate_keys(self, file_path: str, content: str) -> List[Issue]:
        """Check for duplicate keys in JSON"""
        issues = []
        
        # Simple regex-based check for duplicate keys
        # This is not perfect but catches common cases
        import re
        
        # Find all keys
        key_pattern = r'"([^"]+)"\s*:'
        keys = re.findall(key_pattern, content)
        
        # Check for duplicates
        seen: Set[str] = set()
        for key in keys:
            if key in seen:
                issues.append(self.create_issue(
                    IssueCategory.BUG,
                    IssueSeverity.WARNING,
                    file_path,
                    1,
                    1,
                    f"Duplicate key '{key}' found in JSON",
                    "Remove duplicate keys. The last occurrence will override previous ones."
                ))
            seen.add(key)
        
        return issues
    
    def _get_max_depth(self, data, current_depth=1) -> int:
        """Get maximum nesting depth of JSON structure"""
        if isinstance(data, dict):
            if not data:
                return current_depth
            return max(self._get_max_depth(v, current_depth + 1) for v in data.values())
        elif isinstance(data, list):
            if not data:
                return current_depth
            return max(self._get_max_depth(item, current_depth + 1) for item in data)
        else:
            return current_depth

# Register the analyzer
from . import AnalyzerRegistry
AnalyzerRegistry.register('json', JSONAnalyzer)
