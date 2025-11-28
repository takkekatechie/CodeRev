"""
LLM-powered code analyzer with batch processing support
Uses configured LLM provider for intelligent code review
"""

from typing import List, Dict, Any, Tuple
from analyzers.base_analyzer import BaseAnalyzer, Issue, IssueCategory, IssueSeverity
from config import Config
from utils import get_logger
from llm_cache import LLMCache
import os

logger = get_logger(__name__)


class LLMAnalyzer(BaseAnalyzer):
    """Analyzer that uses LLM for code review with batch processing"""
    
    # Shared cache across all instances
    _cache = LLMCache(ttl_seconds=3600)
    
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
    
    def analyze_files_batch(self, files: List[Tuple[str, str]]) -> Dict[str, List[Issue]]:
        """
        Analyze multiple files in batch for better performance
        
        Args:
            files: List of (file_path, content) tuples
        
        Returns:
            Dict mapping file paths to their issues
        """
        if not self.is_available():
            return {path: [] for path, _ in files}
        
        results = {}
        
        # Check cache first
        uncached_files = []
        for file_path, content in files:
            cached_issues = self._cache.get(file_path, content)
            if cached_issues is not None:
                # Convert cached dict issues to Issue objects
                results[file_path] = self._convert_to_issues(file_path, cached_issues)
                logger.debug(f"Cache hit for {file_path}")
            else:
                uncached_files.append((file_path, content))
        
        if not uncached_files:
            return results
        
        # Create batches of files to analyze
        batches = self._create_batches(uncached_files, batch_size=5)
        
        for batch in batches:
            try:
                # Prepare batch data
                batch_data = []
                for file_path, content in batch:
                    ext = os.path.splitext(file_path)[1].lower()
                    language = self._get_language(ext)
                    batch_data.append({
                        'path': file_path,
                        'content': content,
                        'language': language
                    })
                
                # Analyze batch
                logger.info(f"Analyzing batch of {len(batch_data)} files with LLM")
                batch_results = self.provider.analyze_code_batch(batch_data)
                
                # Process results
                for file_path, content in batch:
                    llm_issues = batch_results.get(file_path, [])
                    
                    # Cache the raw results
                    self._cache.set(file_path, content, llm_issues)
                    
                    # Convert to Issue objects
                    results[file_path] = self._convert_to_issues(file_path, llm_issues)
                    
            except Exception as e:
                logger.error(f"Batch analysis failed: {e}")
                # Return empty results for failed batch
                for file_path, _ in batch:
                    results[file_path] = []
        
        return results
    
    def analyze_file(self, file_path: str, content: str) -> List[Issue]:
        """Analyze single file (fallback for non-batch calls)"""
        if not self.is_available():
            return []
        
        # Check cache first
        cached_issues = self._cache.get(file_path, content)
        if cached_issues is not None:
            logger.debug(f"Cache hit for {file_path}")
            return self._convert_to_issues(file_path, cached_issues)
        
        try:
            # Determine language
            ext = os.path.splitext(file_path)[1].lower()
            language = self._get_language(ext)
            
            # Get issues from LLM
            llm_issues = self.provider.analyze_code(file_path, content, language)
            
            # Cache the results
            self._cache.set(file_path, content, llm_issues)
            
            # Convert to Issue objects
            issues = self._convert_to_issues(file_path, llm_issues)
            
            logger.info(f"LLM analysis found {len(issues)} issues in {file_path}")
            return issues
            
        except Exception as e:
            logger.error(f"LLM analysis failed for {file_path}: {e}")
            return []
    
    def _create_batches(self, files: List[Tuple[str, str]], batch_size: int = 5) -> List[List[Tuple[str, str]]]:
        """Group files into batches"""
        batches = []
        current_batch = []
        current_tokens = 0
        max_tokens_per_batch = 6000  # Leave room for response
        
        for file_path, content in files:
            # Estimate tokens (rough: 1 token ≈ 4 chars)
            file_tokens = len(content) // 4
            
            # If adding this file would exceed limits, start new batch
            if (len(current_batch) >= batch_size or 
                current_tokens + file_tokens > max_tokens_per_batch):
                if current_batch:
                    batches.append(current_batch)
                current_batch = []
                current_tokens = 0
            
            current_batch.append((file_path, content))
            current_tokens += file_tokens
        
        # Add remaining files
        if current_batch:
            batches.append(current_batch)
        
        return batches
    
    def _get_language(self, ext: str) -> str:
        """Map file extension to language"""
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
        return language_map.get(ext, 'unknown')
    
    def _convert_to_issues(self, file_path: str, llm_issues: List[Dict[str, Any]]) -> List[Issue]:
        """Convert LLM response to Issue objects"""
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
        
        return issues
