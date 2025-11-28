"""
Go analyzer for detecting Go code issues
"""

import re
from typing import List
from .base_analyzer import BaseAnalyzer, Issue, IssueCategory, IssueSeverity

class GoAnalyzer(BaseAnalyzer):
    """Analyzer for Go files"""
    
    def get_supported_extensions(self) -> List[str]:
        return ['.go']
    
    def analyze_file(self, file_path: str, content: str) -> List[Issue]:
        """Analyze Go file"""
        issues = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Security: Check for hardcoded credentials
            if re.search(r'(password|secret|token|api[_-]?key)\s*[:=]\s*["\'][\w\-]{8,}["\']', line, re.IGNORECASE):
                issues.append(self.create_issue(
                    IssueCategory.SECURITY,
                    IssueSeverity.ERROR,
                    file_path,
                    line_num,
                    line_num,
                    "Potential hardcoded credential detected",
                    "Use environment variables or secure configuration management for credentials."
                ))
            
            # Security: SQL injection risk
            if 'Exec(' in line or 'Query(' in line:
                if '+' in line or 'fmt.Sprintf' in line:
                    issues.append(self.create_issue(
                        IssueCategory.SECURITY,
                        IssueSeverity.ERROR,
                        file_path,
                        line_num,
                        line_num,
                        "Potential SQL injection vulnerability",
                        "Use parameterized queries instead of string concatenation."
                    ))
            
            # Bug: Unchecked error
            if re.search(r'^\s*[a-zA-Z_]\w*\s*,\s*_\s*:?=', line):
                issues.append(self.create_issue(
                    IssueCategory.BUG,
                    IssueSeverity.WARNING,
                    file_path,
                    line_num,
                    line_num,
                    "Error value ignored",
                    "Always check error return values in Go."
                ))
            
            # Bug: Empty error check
            if re.search(r'if\s+err\s*!=\s*nil\s*{\s*}', line):
                issues.append(self.create_issue(
                    IssueCategory.BUG,
                    IssueSeverity.ERROR,
                    file_path,
                    line_num,
                    line_num,
                    "Empty error check block",
                    "Handle errors appropriately instead of ignoring them."
                ))
            
            # Performance: Inefficient string concatenation in loop
            if 'for ' in line and ('+=' in line or '= ' in line) and '"' in line:
                issues.append(self.create_issue(
                    IssueCategory.PERFORMANCE,
                    IssueSeverity.WARNING,
                    file_path,
                    line_num,
                    line_num,
                    "String concatenation in loop",
                    "Use strings.Builder for efficient string concatenation in loops."
                ))
            
            # Maintainability: TODO/FIXME comments
            if re.search(r'//\s*(TODO|FIXME|HACK|XXX)', line, re.IGNORECASE):
                issues.append(self.create_issue(
                    IssueCategory.MAINTAINABILITY,
                    IssueSeverity.INFO,
                    file_path,
                    line_num,
                    line_num,
                    f"Found {re.search(r'(TODO|FIXME|HACK|XXX)', line, re.IGNORECASE).group(1)} comment",
                    "Address or document these items for better code maintainability."
                ))
            
            # Maintainability: Exported function without comment
            if re.match(r'^func\s+[A-Z]\w+', line):
                # Check if previous line has a comment
                if line_num > 1 and not lines[line_num - 2].strip().startswith('//'):
                    issues.append(self.create_issue(
                        IssueCategory.MAINTAINABILITY,
                        IssueSeverity.INFO,
                        file_path,
                        line_num,
                        line_num,
                        "Exported function without documentation comment",
                        "Add a comment describing what this exported function does."
                    ))
            
            # Security: Use of unsafe package
            if 'import "unsafe"' in line or 'import unsafe' in line:
                issues.append(self.create_issue(
                    IssueCategory.SECURITY,
                    IssueSeverity.WARNING,
                    file_path,
                    line_num,
                    line_num,
                    "Use of unsafe package",
                    "Avoid using the unsafe package unless absolutely necessary."
                ))
        
        return issues
