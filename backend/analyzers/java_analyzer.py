"""
Java analyzer for detecting Java code issues
"""

import re
from typing import List
from .base_analyzer import BaseAnalyzer, Issue, IssueCategory, IssueSeverity

class JavaAnalyzer(BaseAnalyzer):
    """Analyzer for Java files"""
    
    def get_supported_extensions(self) -> List[str]:
        return ['.java']
    
    def analyze_file(self, file_path: str, content: str) -> List[Issue]:
        """Analyze Java file"""
        issues = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Security: Check for hardcoded credentials
            if re.search(r'(password|secret|token|api[_-]?key)\s*=\s*["\'][\w\-]{8,}["\']', line, re.IGNORECASE):
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
            if 'executeQuery(' in line or 'executeUpdate(' in line:
                if '+' in line or 'String.format' in line:
                    issues.append(self.create_issue(
                        IssueCategory.SECURITY,
                        IssueSeverity.ERROR,
                        file_path,
                        line_num,
                        line_num,
                        "Potential SQL injection vulnerability",
                        "Use PreparedStatement with parameterized queries instead of string concatenation."
                    ))
            
            # Security: Deserialization vulnerability
            if 'ObjectInputStream' in line and 'readObject' in line:
                issues.append(self.create_issue(
                    IssueCategory.SECURITY,
                    IssueSeverity.WARNING,
                    file_path,
                    line_num,
                    line_num,
                    "Unsafe deserialization detected",
                    "Validate and sanitize deserialized objects to prevent remote code execution."
                ))
            
            # Bug: Empty catch block
            if re.search(r'catch\s*\([^)]+\)\s*{\s*}', line):
                issues.append(self.create_issue(
                    IssueCategory.BUG,
                    IssueSeverity.WARNING,
                    file_path,
                    line_num,
                    line_num,
                    "Empty catch block",
                    "Handle exceptions appropriately or at least log them."
                ))
            
            # Bug: Catching generic Exception
            if re.search(r'catch\s*\(\s*Exception\s+\w+\s*\)', line):
                issues.append(self.create_issue(
                    IssueCategory.BUG,
                    IssueSeverity.INFO,
                    file_path,
                    line_num,
                    line_num,
                    "Catching generic Exception",
                    "Catch specific exception types instead of generic Exception."
                ))
            
            # Bug: Comparison using == for strings
            if re.search(r'(String|str)\s+\w+\s*==', line) or re.search(r'==\s*["\']', line):
                issues.append(self.create_issue(
                    IssueCategory.BUG,
                    IssueSeverity.WARNING,
                    file_path,
                    line_num,
                    line_num,
                    "String comparison using == instead of .equals()",
                    "Use .equals() method for string comparison instead of == operator."
                ))
            
            # Performance: String concatenation in loop
            if ('for(' in line or 'for (' in line or 'while(' in line or 'while (' in line):
                if '+=' in line and '"' in line:
                    issues.append(self.create_issue(
                        IssueCategory.PERFORMANCE,
                        IssueSeverity.WARNING,
                        file_path,
                        line_num,
                        line_num,
                        "String concatenation in loop",
                        "Use StringBuilder for efficient string concatenation in loops."
                    ))
            
            # Performance: Inefficient collection usage
            if 'Vector' in line and 'new Vector' in line:
                issues.append(self.create_issue(
                    IssueCategory.PERFORMANCE,
                    IssueSeverity.INFO,
                    file_path,
                    line_num,
                    line_num,
                    "Use of legacy Vector class",
                    "Use ArrayList instead of Vector for better performance in non-threaded contexts."
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
            
            # Maintainability: Public method without Javadoc
            if re.match(r'^\s*public\s+\w+\s+\w+\s*\(', line):
                # Check if previous line has a Javadoc comment
                if line_num > 1 and not lines[line_num - 2].strip().startswith('/**'):
                    issues.append(self.create_issue(
                        IssueCategory.MAINTAINABILITY,
                        IssueSeverity.INFO,
                        file_path,
                        line_num,
                        line_num,
                        "Public method without Javadoc comment",
                        "Add Javadoc comments for public methods to improve code documentation."
                    ))
            
            # Bug: Potential NullPointerException
            if re.search(r'\.\w+\(\)', line) and 'null' in line.lower():
                issues.append(self.create_issue(
                    IssueCategory.BUG,
                    IssueSeverity.INFO,
                    file_path,
                    line_num,
                    line_num,
                    "Potential NullPointerException",
                    "Add null checks before method calls or use Optional."
                ))
            
            # Security: Use of Random instead of SecureRandom
            if 'new Random()' in line and ('password' in content.lower() or 'token' in content.lower()):
                issues.append(self.create_issue(
                    IssueCategory.SECURITY,
                    IssueSeverity.WARNING,
                    file_path,
                    line_num,
                    line_num,
                    "Use of Random for security-sensitive operations",
                    "Use SecureRandom instead of Random for cryptographic operations."
                ))
        
        return issues
