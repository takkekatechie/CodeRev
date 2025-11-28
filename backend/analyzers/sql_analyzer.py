"""
SQL analyzer for detecting SQL issues
"""

import re
from typing import List
from .base_analyzer import BaseAnalyzer, Issue, IssueCategory, IssueSeverity
import sqlparse

class SQLAnalyzer(BaseAnalyzer):
    """Analyzer for SQL files"""
    
    def get_supported_extensions(self) -> List[str]:
        return ['.sql']
    
    def analyze_file(self, file_path: str, content: str) -> List[Issue]:
        """Analyze SQL file"""
        issues = []
        
        try:
            # Parse SQL
            statements = sqlparse.parse(content)
            
            for stmt in statements:
                issues.extend(self._check_sql_statement(file_path, stmt))
            
            # Additional pattern-based checks
            issues.extend(self._check_sql_patterns(file_path, content))
            
        except Exception as e:
            # If parsing fails, still do pattern-based checks
            issues.extend(self._check_sql_patterns(file_path, content))
        
        return issues
    
    def _check_sql_statement(self, file_path: str, stmt: sqlparse.sql.Statement) -> List[Issue]:
        """Check individual SQL statement"""
        issues = []
        
        stmt_str = str(stmt).upper()
        
        # Check for SELECT *
        if 'SELECT *' in stmt_str or 'SELECT*' in stmt_str:
            issues.append(self.create_issue(
                IssueCategory.PERFORMANCE,
                IssueSeverity.WARNING,
                file_path,
                1,  # Would need better line tracking
                1,
                "SELECT * is inefficient and can cause issues",
                "Explicitly list the columns you need instead of using SELECT *."
            ))
        
        # Check for missing WHERE clause in DELETE/UPDATE
        if stmt_str.startswith('DELETE') or stmt_str.startswith('UPDATE'):
            if 'WHERE' not in stmt_str:
                issues.append(self.create_issue(
                    IssueCategory.BUG,
                    IssueSeverity.ERROR,
                    file_path,
                    1,
                    1,
                    f"{stmt_str.split()[0]} statement without WHERE clause",
                    "Add a WHERE clause to avoid affecting all rows unintentionally."
                ))
        
        return issues
    
    def _check_sql_patterns(self, file_path: str, content: str) -> List[Issue]:
        """Pattern-based SQL checks"""
        issues = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line_upper = line.upper()
            
            # Check for CROSS JOIN without limits
            if 'CROSS JOIN' in line_upper and 'LIMIT' not in content.upper():
                issues.append(self.create_issue(
                    IssueCategory.PERFORMANCE,
                    IssueSeverity.WARNING,
                    file_path,
                    line_num,
                    line_num,
                    "CROSS JOIN without LIMIT can produce huge result sets",
                    "Add a LIMIT clause or reconsider if CROSS JOIN is necessary."
                ))
            
            # Check for OR in WHERE clause (can prevent index usage)
            if re.search(r'WHERE.*\bOR\b', line_upper):
                issues.append(self.create_issue(
                    IssueCategory.PERFORMANCE,
                    IssueSeverity.INFO,
                    file_path,
                    line_num,
                    line_num,
                    "OR in WHERE clause may prevent index usage",
                    "Consider using UNION or restructuring the query for better performance."
                ))
        
        return issues
