"""
LLM-powered code analyzer
Uses configured LLM provider for intelligent code review
"""

from typing import List, Dict, Any
from analyzers.base_analyzer import BaseAnalyzer, Issue, IssueCategory, IssueSeverity
from config import Config
from utils import get_logger
import os

logger = get_logger(__name__)


class LLMAnalyzer(BaseAnalyzer):
    """Analyzer that uses LLM for code review"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.provider = None
        self.llm_available = False
        self._initialize_provider()
    
    def _initialize_provider(self):
        """Initialize the LLM provider"""
        try:
            # Load LLM config if not already loaded
            if not Config.LLM_ENABLED:
                Config.load_llm_config()
            
            if not Config.LLM_ENABLED:
                logger.info("LLM analysis disabled in configuration")
                return
            
            # Get provider
            from llm_providers import get_provider
            
            provider_config = Config.get_llm_provider_config()
            if not provider_config:
                logger.warning(f"No configuration found for provider: {Config.LLM_PROVIDER}")
                return
            
            # Add common settings to provider config
            provider_config['rate_limit'] = Config.LLM_CONFIG.get('rate_limit', {})
            
            self.provider = get_provider(Config.LLM_PROVIDER, provider_config)
            
            # Check availability
            if self.provider.check_availability():
                self.llm_available = True
                logger.info(f"LLM provider '{Config.LLM_PROVIDER}' initialized successfully")
            else:
                logger.warning(f"LLM provider '{Config.LLM_PROVIDER}' not available")
                
        except Exception as e:
            logger.error(f"Failed to initialize LLM provider: {e}")
            self.provider = None
            self.llm_available = False
    
    def get_supported_extensions(self) -> List[str]:
        """LLM can analyze all supported file types"""
        return ['.py', '.pyw', '.js', '.jsx', '.ts', '.tsx', '.mjs', '.sql', '.json']
    
    def is_available(self) -> bool:
        """Check if LLM is available for analysis"""
        if not self.llm_available or not self.provider:
            return False
        
        # Check credits/quota
        try:
            return self.provider.check_credits()
        except Exception:
            return False
    
    def analyze_file(self, file_path: str, content: str) -> List[Issue]:
        """Analyze file using LLM"""
        if not self.is_available():
            return []
        
        try:
            # Determine language from file extension
            ext = os.path.splitext(file_path)[1].lower()
            language_map = {
                '.py': 'python',
                '.pyw': 'python',
                '.js': 'javascript',
                '.jsx': 'javascript',
                '.ts': 'typescript',
                '.tsx': 'typescript',
                '.mjs': 'javascript',
                '.sql': 'sql',
                '.json': 'json'
            }
            language = language_map.get(ext, 'unknown')
            
            # Get issues from LLM
            llm_issues = self.provider.analyze_code(file_path, content, language)
            
            # Convert to Issue objects
            issues = []
            for llm_issue in llm_issues:
                try:
                    # Map category
                    category_map = {
                        'security': IssueCategory.SECURITY,
                        'bug': IssueCategory.BUG,
                        'performance': IssueCategory.PERFORMANCE,
                        'maintainability': IssueCategory.MAINTAINABILITY,
                        'architecture': IssueCategory.ARCHITECTURE,
                    }
                    category = category_map.get(
                        llm_issue.get('category', 'maintainability').lower(),
                        IssueCategory.MAINTAINABILITY
                    )
                    
                    # Map severity
                    severity_map = {
                        'error': IssueSeverity.ERROR,
                        'warning': IssueSeverity.WARNING,
                        'info': IssueSeverity.INFO,
                    }
                    severity = severity_map.get(
                        llm_issue.get('severity', 'info').lower(),
                        IssueSeverity.INFO
                    )
                    
                    issue = self.create_issue(
                        category=category,
                        severity=severity,
                        file_path=file_path,
                        line_start=llm_issue.get('line_start', 1),
                        line_end=llm_issue.get('line_end', 1),
                        description=llm_issue.get('description', 'Issue detected by LLM'),
                        recommendation=llm_issue.get('recommendation', '')
                    )
                    issues.append(issue)
                    
                except Exception as e:
                    logger.error(f"Error converting LLM issue: {e}")
                    continue
            
            logger.info(f"LLM analysis found {len(issues)} issues in {file_path}")
            return issues
            
        except Exception as e:
            logger.error(f"LLM analysis failed for {file_path}: {e}")
            return []
