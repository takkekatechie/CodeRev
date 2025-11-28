"""
Analyzer registry and management
"""

from typing import List, Type
from .base_analyzer import BaseAnalyzer
from .python_analyzer import PythonAnalyzer
from .javascript_analyzer import JavaScriptAnalyzer
from .sql_analyzer import SQLAnalyzer
from .json_analyzer import JSONAnalyzer
from .llm_analyzer import LLMAnalyzer
from .go_analyzer import GoAnalyzer
from .rust_analyzer import RustAnalyzer
from .java_analyzer import JavaAnalyzer


class AnalyzerRegistry:
    """Registry for all code analyzers"""
    
    # Analyzers in priority order (LLM first, then pattern-based)
    _analyzers = [
        LLMAnalyzer,  # Try LLM first if available
        PythonAnalyzer,
        JavaScriptAnalyzer,
        JavaAnalyzer,
        GoAnalyzer,
        RustAnalyzer,
        SQLAnalyzer,
        JSONAnalyzer,
    ]
    
    @classmethod
    def get_all_analyzers(cls) -> List[Type[BaseAnalyzer]]:
        """Get all registered analyzers"""
        return cls._analyzers
    
    @classmethod
    def get_analyzers_for_file(cls, file_path: str) -> List[Type[BaseAnalyzer]]:
        """Get analyzers that can handle the given file"""
        analyzers = []
        for analyzer_class in cls._analyzers:
            analyzer = analyzer_class()
            if analyzer.can_analyze(file_path):
                # Special handling for LLM analyzer
                if isinstance(analyzer, LLMAnalyzer):
                    if analyzer.is_available():
                        analyzers.append(analyzer_class)
                else:
                    analyzers.append(analyzer_class)
        return analyzers


__all__ = ['BaseAnalyzer', 'AnalyzerRegistry']
