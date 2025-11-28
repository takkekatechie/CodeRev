"""
Rust analyzer for detecting Rust code issues
"""

import re
from typing import List
from .base_analyzer import BaseAnalyzer, Issue, IssueCategory, IssueSeverity

class RustAnalyzer(BaseAnalyzer):
    """Analyzer for Rust files"""
    
    def get_supported_extensions(self) -> List[str]:
        return ['.rs']
    
    def analyze_file(self, file_path: str, content: str) -> List[Issue]:
        """Analyze Rust file"""
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
            
            # Security: Unsafe block usage
            if re.match(r'^\s*unsafe\s*{', line):
                issues.append(self.create_issue(
                    IssueCategory.SECURITY,
                    IssueSeverity.WARNING,
                    file_path,
                    line_num,
                    line_num,
                    "Use of unsafe block",
                    "Ensure unsafe code is necessary and well-documented. Consider safe alternatives."
                ))
            
            # Bug: unwrap() usage
            if '.unwrap()' in line:
                issues.append(self.create_issue(
                    IssueCategory.BUG,
                    IssueSeverity.WARNING,
                    file_path,
                    line_num,
                    line_num,
                    "Use of unwrap() can cause panic",
                    "Use pattern matching, if let, or expect() with a descriptive message instead."
                ))
            
            # Bug: expect() without meaningful message
            if re.search(r'\.expect\(["\']["\']', line):
                issues.append(self.create_issue(
                    IssueCategory.BUG,
                    IssueSeverity.INFO,
                    file_path,
                    line_num,
                    line_num,
                    "expect() called with empty message",
                    "Provide a meaningful error message to expect()."
                ))
            
            # Performance: Clone in loop
            if 'for ' in line and '.clone()' in line:
                issues.append(self.create_issue(
                    IssueCategory.PERFORMANCE,
                    IssueSeverity.WARNING,
                    file_path,
                    line_num,
                    line_num,
                    "Cloning in loop may impact performance",
                    "Consider using references or restructuring to avoid unnecessary clones."
                ))
            
            # Performance: Inefficient string concatenation
            if re.search(r'\+\s*&', line) and 'String' in line:
                issues.append(self.create_issue(
                    IssueCategory.PERFORMANCE,
                    IssueSeverity.INFO,
                    file_path,
                    line_num,
                    line_num,
                    "String concatenation with + operator",
                    "Use format!() macro or String::push_str() for better performance."
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
            
            # Maintainability: Public function without documentation
            if re.match(r'^\s*pub\s+fn\s+\w+', line):
                # Check if previous line has a doc comment
                if line_num > 1 and not lines[line_num - 2].strip().startswith('///'):
                    issues.append(self.create_issue(
                        IssueCategory.MAINTAINABILITY,
                        IssueSeverity.INFO,
                        file_path,
                        line_num,
                        line_num,
                        "Public function without documentation comment",
                        "Add /// documentation comments for public APIs."
                    ))
            
            # Bug: Potential panic with indexing
            if re.search(r'\[\d+\]', line) and 'vec!' not in line.lower():
                issues.append(self.create_issue(
                    IssueCategory.BUG,
                    IssueSeverity.INFO,
                    file_path,
                    line_num,
                    line_num,
                    "Direct indexing can panic if out of bounds",
                    "Consider using .get() method which returns Option instead."
                ))
            
            # Security: println! with user input
            if 'println!' in line and ('input' in line.lower() or 'user' in line.lower()):
                issues.append(self.create_issue(
                    IssueCategory.SECURITY,
                    IssueSeverity.INFO,
                    file_path,
                    line_num,
                    line_num,
                    "Printing user input directly",
                    "Ensure user input is sanitized before printing to prevent injection attacks."
                ))
        
        return issues
