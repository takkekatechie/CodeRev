"""
JavaScript/TypeScript analyzer with React and React Native support
"""

import re
from typing import List
from analyzers.base_analyzer import BaseAnalyzer, Issue, IssueCategory, IssueSeverity

class JavaScriptAnalyzer(BaseAnalyzer):
    """Analyzes JavaScript and TypeScript files including React/React Native"""
    
    def get_supported_extensions(self) -> List[str]:
        return ['.js', '.jsx', '.ts', '.tsx', '.mjs']
    
    def analyze_file(self, file_path: str, content: str) -> List[Issue]:
        """Analyze JavaScript/TypeScript file"""
        issues = []
        
        # Detect if it's a React file
        is_react = 'import React' in content or 'from \'react\'' in content or 'from "react"' in content
        is_react_native = 'react-native' in content
        
        # Common checks
        issues.extend(self._check_security(file_path, content))
        issues.extend(self._check_bugs(file_path, content))
        issues.extend(self._check_performance(file_path, content))
        
        # React-specific checks
        if is_react or is_react_native:
            issues.extend(self._check_react_issues(file_path, content, is_react_native))
        
        return issues
    
    def _check_security(self, file_path: str, content: str) -> List[Issue]:
        """Check for security issues"""
        issues = []
        lines = content.split('\n')
        
        # Check for hardcoded secrets
        secret_patterns = [
            (r'(api[_-]?key|apikey)\s*[:=]\s*["\']([^"\']{20,})["\']', 'Hardcoded API key'),
            (r'(secret|password|token)\s*[:=]\s*["\']([^"\']{8,})["\']', 'Hardcoded secret'),
        ]
        
        for line_num, line in enumerate(lines[:500], 1):
            for pattern, desc in secret_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(self.create_issue(
                        IssueCategory.SECURITY,
                        IssueSeverity.ERROR,
                        file_path,
                        line_num,
                        line_num,
                        f"{desc} detected",
                        "Move secrets to environment variables (.env file)"
                    ))
                    break
        
        # Check for dangerous functions
        dangerous_patterns = [
            (r'eval\s*\(', 'Use of eval() is dangerous'),
            (r'dangerouslySetInnerHTML', 'Use of dangerouslySetInnerHTML can lead to XSS'),
            (r'innerHTML\s*=', 'Direct innerHTML assignment can lead to XSS'),
        ]
        
        for line_num, line in enumerate(lines, 1):
            for pattern, desc in dangerous_patterns:
                if re.search(pattern, line):
                    issues.append(self.create_issue(
                        IssueCategory.SECURITY,
                        IssueSeverity.WARNING,
                        file_path,
                        line_num,
                        line_num,
                        desc,
                        "Use safer alternatives or sanitize input"
                    ))
        
        return issues
    
    def _check_bugs(self, file_path: str, content: str) -> List[Issue]:
        """Check for common bugs"""
        issues = []
        lines = content.split('\n')
        
        # Check for == instead of ===
        for line_num, line in enumerate(lines, 1):
            if re.search(r'[^=!<>]==[^=]', line) and '//' not in line[:line.find('==')]:
                issues.append(self.create_issue(
                    IssueCategory.BUG,
                    IssueSeverity.WARNING,
                    file_path,
                    line_num,
                    line_num,
                    "Use === instead of == for comparison",
                    "Use strict equality (===) to avoid type coercion bugs"
                ))
        
        # Check for console.log in production code
        for line_num, line in enumerate(lines, 1):
            if re.search(r'console\.(log|debug|info)', line) and not line.strip().startswith('//'):
                issues.append(self.create_issue(
                    IssueCategory.MAINTAINABILITY,
                    IssueSeverity.INFO,
                    file_path,
                    line_num,
                    line_num,
                    "Console statement found",
                    "Remove console statements before production deployment"
                ))
        
        return issues
    
    def _check_performance(self, file_path: str, content: str) -> List[Issue]:
        """Check for performance issues"""
        issues = []
        lines = content.split('\n')
        
        # Check for inefficient array operations
        for line_num, line in enumerate(lines, 1):
            # Multiple array iterations
            if line.count('.map(') + line.count('.filter(') + line.count('.forEach(') > 1:
                issues.append(self.create_issue(
                    IssueCategory.PERFORMANCE,
                    IssueSeverity.INFO,
                    file_path,
                    line_num,
                    line_num,
                    "Multiple array iterations on same line",
                    "Consider combining operations or using a single loop"
                ))
        
        return issues
    
    def _check_react_issues(self, file_path: str, content: str, is_react_native: bool) -> List[Issue]:
        """Check for React-specific issues"""
        issues = []
        lines = content.split('\n')
        
        # Check for missing key prop in lists
        for line_num, line in enumerate(lines, 1):
            if '.map(' in line and 'return' in line and 'key=' not in line:
                # Look ahead a few lines for the key prop
                has_key = any('key=' in lines[i] for i in range(line_num, min(line_num + 3, len(lines))))
                if not has_key:
                    issues.append(self.create_issue(
                        IssueCategory.BUG,
                        IssueSeverity.WARNING,
                        file_path,
                        line_num,
                        line_num,
                        "Missing 'key' prop in list rendering",
                        "Add a unique 'key' prop to elements in a list"
                    ))
        
        # Check for inline function definitions in JSX
        for line_num, line in enumerate(lines, 1):
            if re.search(r'(onClick|onPress|onChange|onSubmit)\s*=\s*\{.*=>', line):
                issues.append(self.create_issue(
                    IssueCategory.PERFORMANCE,
                    IssueSeverity.INFO,
                    file_path,
                    line_num,
                    line_num,
                    "Inline function in JSX prop",
                    "Define function outside render or use useCallback to avoid re-renders"
                ))
        
        # Check for missing useEffect dependencies
        in_use_effect = False
        use_effect_start = 0
        for line_num, line in enumerate(lines, 1):
            if 'useEffect(' in line:
                in_use_effect = True
                use_effect_start = line_num
            elif in_use_effect and '], [])' in line:
                in_use_effect = False
            elif in_use_effect and '])' in line and '[]' not in line:
                in_use_effect = False
        
        # Check for useState with objects (should use multiple states)
        for line_num, line in enumerate(lines, 1):
            if re.search(r'useState\s*\(\s*\{', line):
                issues.append(self.create_issue(
                    IssueCategory.MAINTAINABILITY,
                    IssueSeverity.INFO,
                    file_path,
                    line_num,
                    line_num,
                    "useState with object",
                    "Consider splitting into multiple useState calls for better performance"
                ))
        
        # React Native specific checks
        if is_react_native:
            # Check for missing accessibility props
            for line_num, line in enumerate(lines, 1):
                if re.search(r'<(TouchableOpacity|Button|Pressable)', line):
                    has_accessibility = any('accessible' in lines[i] for i in range(line_num, min(line_num + 5, len(lines))))
                    if not has_accessibility:
                        issues.append(self.create_issue(
                            IssueCategory.MAINTAINABILITY,
                            IssueSeverity.INFO,
                            file_path,
                            line_num,
                            line_num,
                            "Missing accessibility props",
                            "Add accessibilityLabel and accessibilityRole for better accessibility"
                        ))
            
            # Check for FlatList without keyExtractor
            for line_num, line in enumerate(lines, 1):
                if '<FlatList' in line:
                    has_key_extractor = any('keyExtractor' in lines[i] for i in range(line_num, min(line_num + 10, len(lines))))
                    if not has_key_extractor:
                        issues.append(self.create_issue(
                            IssueCategory.PERFORMANCE,
                            IssueSeverity.WARNING,
                            file_path,
                            line_num,
                            line_num,
                            "FlatList without keyExtractor",
                            "Add keyExtractor prop for better performance"
                        ))
        
        return issues
