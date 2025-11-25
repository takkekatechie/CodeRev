"""
Base analyzer interface for all code analyzers
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from dataclasses import dataclass
from enum import Enum

class IssueCategory(Enum):
    """Issue categories"""
    BUG = 'bug'
    SECURITY = 'security'
    PERFORMANCE = 'performance'
    MAINTAINABILITY = 'maintainability'
    ARCHITECTURE = 'architecture'

class IssueSeverity(Enum):
    """Issue severity levels"""
    ERROR = 'error'
    WARNING = 'warning'
    INFO = 'info'

@dataclass
class Issue:
    """Represents a code issue"""
    category: str
    severity: str
    file_path: str
    line_start: int
    line_end: int
    description: str
    recommendation: str = None
    code_snippet: str = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'category': self.category,
            'severity': self.severity,
            'file_path': self.file_path,
            'line_start': self.line_start,
            'line_end': self.line_end,
            'description': self.description,
            'recommendation': self.recommendation,
            'code_snippet': self.code_snippet,
        }

class BaseAnalyzer(ABC):
    """Base class for all analyzers"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.issues: List[Issue] = []
    
    @abstractmethod
    def analyze_file(self, file_path: str, content: str) -> List[Issue]:
        """
        Analyze a single file
        Returns list of issues found
        """
        pass
    
    @abstractmethod
    def get_supported_extensions(self) -> List[str]:
        """
        Get list of file extensions this analyzer supports
        Returns list of extensions (e.g., ['.py', '.pyw'])
        """
        pass
    
    def can_analyze(self, file_path: str) -> bool:
        """Check if this analyzer can analyze the given file"""
        from pathlib import Path
        ext = Path(file_path).suffix.lower()
        return ext in self.get_supported_extensions()
    
    def create_issue(
        self,
        category: IssueCategory,
        severity: IssueSeverity,
        file_path: str,
        line_start: int,
        line_end: int,
        description: str,
        recommendation: str = None,
        code_snippet: str = None
    ) -> Issue:
        """Helper to create an issue"""
        return Issue(
            category=category.value,
            severity=severity.value,
            file_path=file_path,
            line_start=line_start,
            line_end=line_end,
            description=description,
            recommendation=recommendation,
            code_snippet=code_snippet
        )
    
    def reset(self) -> None:
        """Reset analyzer state"""
        self.issues = []
