"""
Python code analyzer using AST and external tools
"""

import ast
import re
from typing import List
from pathlib import Path
from .base_analyzer import BaseAnalyzer, Issue, IssueCategory, IssueSeverity

class PythonAnalyzer(BaseAnalyzer):
    """Analyzer for Python code"""
    
    def get_supported_extensions(self) -> List[str]:
        return ['.py', '.pyw']
    
    def analyze_file(self, file_path: str, content: str) -> List[Issue]:
        """Analyze Python file"""
        issues = []
        
        try:
            # Parse AST
            tree = ast.parse(content, filename=file_path)
            
            # Run various checks
            issues.extend(self._check_security(file_path, content, tree))
            issues.extend(self._check_bugs(file_path, content, tree))
            issues.extend(self._check_maintainability(file_path, content, tree))
            issues.extend(self._check_performance(file_path, content, tree))
            
        except SyntaxError as e:
            issues.append(self.create_issue(
                IssueCategory.BUG,
                IssueSeverity.ERROR,
                file_path,
                e.lineno or 1,
                e.lineno or 1,
                f"Syntax error: {e.msg}",
                "Fix the syntax error to make the code valid Python."
            ))
        
        return issues
    
    def _check_security(self, file_path: str, content: str, tree: ast.AST) -> List[Issue]:
        """Check for security issues (OPTIMIZED)"""
        issues = []
        lines = content.split('\n')
        
        # Check for hardcoded secrets (limited patterns)
        secret_patterns = [
            (r'password\s*=\s*["\']([^"\']{8,})["\']', 'Hardcoded password'),
            (r'api[_-]?key\s*=\s*["\']([^"\']{20,})["\']', 'Hardcoded API key'),
        ]
        
        for line_num, line in enumerate(lines[:500], 1):  # Limit to first 500 lines
            for pattern, desc in secret_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(self.create_issue(
                        IssueCategory.SECURITY,
                        IssueSeverity.ERROR,
                        file_path,
                        line_num,
                        line_num,
                        f"{desc} detected in source code",
                        "Move sensitive credentials to environment variables."
                    ))
                    break  # One issue per line max
        
        # Quick AST checks (limited)
        for node in ast.walk(tree):
            # Check for eval/exec
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in ['eval', 'exec']:
                    issues.append(self.create_issue(
                        IssueCategory.SECURITY,
                        IssueSeverity.WARNING,
                        file_path,
                        node.lineno,
                        node.end_lineno or node.lineno,
                        f"Use of '{node.func.id}' function can be dangerous",
                        f"Avoid using {node.func.id}()."
                    ))
        
        return issues
    
    def _check_bugs(self, file_path: str, content: str, tree: ast.AST) -> List[Issue]:
        """Check for common bugs"""
        issues = []
        
        # Check for bare except clauses
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    issues.append(self.create_issue(
                        IssueCategory.BUG,
                        IssueSeverity.WARNING,
                        file_path,
                        node.lineno,
                        node.end_lineno or node.lineno,
                        "Bare except clause catches all exceptions",
                        "Specify the exception type(s) to catch. Use 'except Exception:' at minimum."
                    ))
        
        # Check for mutable default arguments
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for default in node.args.defaults:
                    if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                        issues.append(self.create_issue(
                            IssueCategory.BUG,
                            IssueSeverity.WARNING,
                            file_path,
                            node.lineno,
                            node.lineno,
                            f"Function '{node.name}' has mutable default argument",
                            "Use None as default and create the mutable object inside the function."
                        ))
        
        return issues
    
    def _check_maintainability(self, file_path: str, content: str, tree: ast.AST) -> List[Issue]:
        """Check maintainability issues"""
        issues = []
        
        # Check function length
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_length = (node.end_lineno or node.lineno) - node.lineno
                if func_length > 50:
                    issues.append(self.create_issue(
                        IssueCategory.MAINTAINABILITY,
                        IssueSeverity.INFO,
                        file_path,
                        node.lineno,
                        node.end_lineno or node.lineno,
                        f"Function '{node.name}' is too long ({func_length} lines)",
                        "Consider breaking this function into smaller, more focused functions."
                    ))
        
        # Check for too many arguments
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                arg_count = len(node.args.args)
                if arg_count > 5:
                    issues.append(self.create_issue(
                        IssueCategory.MAINTAINABILITY,
                        IssueSeverity.INFO,
                        file_path,
                        node.lineno,
                        node.lineno,
                        f"Function '{node.name}' has too many parameters ({arg_count})",
                        "Consider using a configuration object or reducing the number of parameters."
                    ))
        
        return issues
    
    def _check_performance(self, file_path: str, content: str, tree: ast.AST) -> List[Issue]:
        """Check performance issues"""
        issues = []
        
        # Check for inefficient string concatenation in loops
        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While)):
                for child in ast.walk(node):
                    if isinstance(child, ast.AugAssign):
                        if isinstance(child.op, ast.Add) and self._is_string_operation(child):
                            issues.append(self.create_issue(
                                IssueCategory.PERFORMANCE,
                                IssueSeverity.WARNING,
                                file_path,
                                child.lineno,
                                child.end_lineno or child.lineno,
                                "String concatenation in loop is inefficient",
                                "Use ''.join() or a list to collect strings, then join them."
                            ))
        
        return issues
    
    def _is_sql_execution(self, node: ast.Call) -> bool:
        """Check if node is a SQL execution call"""
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in ['execute', 'executemany', 'raw']:
                return True
        return False
    
    def _has_string_formatting(self, node: ast.Call) -> bool:
        """Check if call uses string formatting"""
        if not node.args:
            return False
        
        first_arg = node.args[0]
        
        # Check for f-strings, % formatting, or .format()
        if isinstance(first_arg, ast.JoinedStr):  # f-string
            return True
        
        if isinstance(first_arg, ast.BinOp) and isinstance(first_arg.op, ast.Mod):  # % formatting
            return True
        
        if isinstance(first_arg, ast.Call):
            if isinstance(first_arg.func, ast.Attribute) and first_arg.func.attr == 'format':
                return True
        
        return False
    
    def _is_string_operation(self, node: ast.AugAssign) -> bool:
        """Check if augmented assignment is a string operation"""
        # This is a simplified check
        return True  # In practice, would need type inference
