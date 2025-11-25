"""
Analyzer registry
"""

from typing import List, Type
from pathlib import Path
from analyzers.base_analyzer import BaseAnalyzer

class AnalyzerRegistry:
    """Registry for all code analyzers"""
    
    _analyzers: List[Type[BaseAnalyzer]] = []
    
    @classmethod
    def register(cls, name: str, analyzer_class: Type[BaseAnalyzer]) -> None:
        """Register an analyzer"""
        if analyzer_class not in cls._analyzers:
            cls._analyzers.append(analyzer_class)
    
    @classmethod
    def get_all_analyzers(cls) -> List[Type[BaseAnalyzer]]:
        """Get all registered analyzers"""
        return cls._analyzers.copy()
    
    @classmethod
    def get_analyzers_for_file(cls, file_path: str) -> List[Type[BaseAnalyzer]]:
        """Get analyzers that support the given file"""
        file_ext = Path(file_path).suffix.lower()
        
        matching_analyzers = []
        for analyzer_class in cls._analyzers:
            analyzer = analyzer_class()
            if file_ext in analyzer.get_supported_extensions():
                matching_analyzers.append(analyzer_class)
        
        return matching_analyzers

__all__ = ['BaseAnalyzer', 'AnalyzerRegistry']
