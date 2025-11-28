"""
Fast code scanner with in-memory storage
"""
import os
import time
import uuid
from typing import List, Dict, Any
from collections import defaultdict

# Import analyzers first
import analyzers.python_analyzer
import analyzers.sql_analyzer
import analyzers.json_analyzer
import analyzers.javascript_analyzer

# Then import registry
from analyzers import AnalyzerRegistry
from utils import get_logger, read_file_safe
from config import Config

logger = get_logger(__name__)

class ScanOrchestrator:
    """Orchestrates code scanning and analysis"""
    
    def __init__(self):
        self.scans = {}  # In-memory storage
        self.current_progress = {}
        
        # Load LLM configuration
        try:
            Config.load_llm_config()
            if Config.LLM_ENABLED:
                logger.info(f"LLM enabled with provider: {Config.LLM_PROVIDER}")
            else:
                logger.info("LLM disabled, using pattern-based analysis only")
        except Exception as e:
            logger.error(f"Failed to load LLM config: {e}")
    
    def start_scan(self, repo_path: str, exclude_patterns: List[str] = None) -> str:
        """Start a scan - returns immediately"""
        scan_id = str(uuid.uuid4())
        
        # Initialize scan
        self.scans[scan_id] = {
            'scan_id': scan_id,
            'repo_path': repo_path,
            'status': 'running',
            'progress': 0,
            'start_time': time.time(),
            'issues': [],
            'total_files': 0,
            'languages': [],
        }
        
        # Run scan synchronously (fast enough now)
        self._run_scan(scan_id, repo_path, exclude_patterns or [])
        
        return scan_id
    
    def _run_scan(self, scan_id: str, repo_path: str, exclude_patterns: List[str]):
        """Run the scan"""
        try:
            scan = self.scans[scan_id]
            
            # Detect languages (fast)
            languages = self._detect_languages(repo_path)
            scan['languages'] = languages
            
            # Collect files (fast with os.walk)
            files = self._collect_files(repo_path, exclude_patterns)
            scan['total_files'] = len(files)
            
            logger.info(f"Scanning {len(files)} files")
            
            # Analyze files
            issues = []
            for i, file_path in enumerate(files):
                file_issues = self._analyze_file(file_path)
                issues.extend(file_issues)
                scan['progress'] = ((i + 1) / len(files)) * 100
            
            scan['issues'] = issues
            scan['status'] = 'completed'
            scan['end_time'] = time.time()
            
            logger.info(f"Scan {scan_id} completed: {len(issues)} issues in {len(files)} files")
            
        except Exception as e:
            logger.error(f"Scan failed: {e}", exc_info=True)
            self.scans[scan_id]['status'] = 'failed'
            self.scans[scan_id]['error'] = str(e)
    
    def _detect_languages(self, repo_path: str) -> List[str]:
        """Quick language detection"""
        extensions = set()
        
        for root, dirs, files in os.walk(repo_path):
            # Skip common excluded dirs
            dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__', 'venv']]
            
            for filename in files[:100]:  # Sample first 100 files
                ext = os.path.splitext(filename)[1].lower()
                if ext:
                    extensions.add(ext)
        
        # Map to languages
        lang_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'react',
            '.ts': 'typescript',
            '.tsx': 'react',
            '.sql': 'sql',
            '.json': 'json',
        }
        
        languages = list(set(lang_map.get(ext, 'unknown') for ext in extensions if ext in lang_map))
        return languages if languages else ['unknown']
    
    def _collect_files(self, repo_path: str, exclude_patterns: List[str]) -> List[str]:
        """Collect files to analyze"""
        files = []
        
        # Get supported extensions
        supported = set()
        for analyzer_class in AnalyzerRegistry.get_all_analyzers():
            analyzer = analyzer_class()
            supported.update(analyzer.get_supported_extensions())
        
        # Walk directory
        for root, dirs, filenames in os.walk(repo_path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__', 'venv', 'dist', 'build']]
            
            for filename in filenames:
                ext = os.path.splitext(filename)[1].lower()
                if ext not in supported:
                    continue
                
                file_path = os.path.join(root, filename)
                
                # Check size
                try:
                    if os.path.getsize(file_path) > Config.MAX_FILE_SIZE:
                        continue
                except OSError:
                    continue
                
                files.append(file_path)
        
        return files
    
    def _analyze_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Analyze a single file with LLM-first strategy"""
        content = read_file_safe(file_path, Config.MAX_FILE_SIZE)
        if not content:
            return []
        
        analyzer_classes = AnalyzerRegistry.get_analyzers_for_file(file_path)
        if not analyzer_classes:
            return []
        
        issues = []
        llm_used = False
        
        # Try LLM analyzer first if available
        for analyzer_class in analyzer_classes:
            try:
                analyzer = analyzer_class()
                
                # Check if this is LLM analyzer
                from analyzers.llm_analyzer import LLMAnalyzer
                if isinstance(analyzer, LLMAnalyzer):
                    if analyzer.is_available():
                        file_issues = analyzer.analyze_file(file_path, content)
                        if file_issues:
                            llm_used = True
                            logger.info(f"LLM analysis successful for {file_path}")
                            # Convert to dict format
                            for issue in file_issues:
                                issues.append({
                                    'category': issue.category,
                                    'severity': issue.severity,
                                    'filePath': issue.file_path,
                                    'lineStart': issue.line_start,
                                    'lineEnd': issue.line_end,
                                    'description': issue.description,
                                    'recommendation': issue.recommendation,
                                })
                            break  # LLM succeeded, skip pattern-based analyzers
                        else:
                            logger.debug(f"LLM returned no issues for {file_path}")
                    else:
                        logger.debug(f"LLM not available for {file_path}")
                else:
                    # Pattern-based analyzer - only use if LLM didn't succeed
                    if not llm_used:
                        file_issues = analyzer.analyze_file(file_path, content)
                        for issue in file_issues:
                            issues.append({
                                'category': issue.category,
                                'severity': issue.severity,
                                'filePath': issue.file_path,
                                'lineStart': issue.line_start,
                                'lineEnd': issue.line_end,
                                'description': issue.description,
                                'recommendation': issue.recommendation,
                            })
                        
            except Exception as e:
                logger.error(f"Analyzer {analyzer_class.__name__} failed: {e}")
                continue
        
        return issues
    
    def get_scan_status(self, scan_id: str) -> Dict[str, Any]:
        """Get scan status"""
        if scan_id not in self.scans:
            return {'error': 'Scan not found'}
        
        scan = self.scans[scan_id]
        return {
            'scanId': scan_id,
            'status': scan['status'],
            'progress': scan.get('progress', 0),
        }
    
    def get_scan_results(self, scan_id: str) -> Dict[str, Any]:
        """Get scan results"""
        if scan_id not in self.scans:
            return {'error': 'Scan not found'}
        
        scan = self.scans[scan_id]
        
        if scan['status'] != 'completed':
            return {'error': 'Scan not completed'}
        
        # Calculate summary
        issues_by_category = defaultdict(int)
        issues_by_severity = defaultdict(int)
        
        for issue in scan['issues']:
            issues_by_category[issue['category']] += 1
            issues_by_severity[issue['severity']] += 1
        
        return {
            'scanId': scan_id,
            'repositoryPath': scan['repo_path'],
            'detectedLanguages': scan['languages'],
            'totalFiles': scan['total_files'],
            'issues': scan['issues'],
            'summary': {
                'totalIssues': len(scan['issues']),
                'issuesByCategory': dict(issues_by_category),
                'issuesBySeverity': dict(issues_by_severity),
            }
        }
