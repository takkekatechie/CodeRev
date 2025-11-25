"""
Configuration management for CodeReviewPro backend
"""

import os
from typing import Dict, Any, List
from pathlib import Path
import yaml

class Config:
    """Configuration manager for CodeReviewPro"""
    
    # Server configuration
    SERVER_HOST = os.getenv('CODEREVIEWPRO_HOST', '0.0.0.0')
    SERVER_PORT = int(os.getenv('CODEREVIEWPRO_PORT', '5000'))
    DEBUG = os.getenv('CODEREVIEWPRO_DEBUG', 'False').lower() == 'true'
    
    # Database configuration
    DATABASE_PATH = os.getenv('CODEREVIEWPRO_DB', 'codereviewpro.db')
    
    # Analysis configuration
    MAX_FILE_SIZE = int(os.getenv('CODEREVIEWPRO_MAX_FILE_SIZE', str(1024 * 1024)))  # 1MB default
    LARGE_REPO_THRESHOLD = int(os.getenv('CODEREVIEWPRO_LARGE_REPO', '5000'))  # 5000 files
    
    # Exclude patterns
    DEFAULT_EXCLUDE_PATTERNS = [
        '**/node_modules/**',
        '**/dist/**',
        '**/build/**',
        '**/.git/**',
        '**/venv/**',
        '**/__pycache__/**',
        '**/target/**',
        '**/bin/**',
        '**/obj/**',
        '**/.vscode/**',
        '**/.idea/**',
    ]
    
    # Severity levels
    SEVERITY_LEVELS = {
        'security': 'error',
        'bug': 'error',
        'performance': 'warning',
        'maintainability': 'info',
        'architecture': 'info',
    }
    
    # Language detection configuration
    LANGUAGE_EXTENSIONS = {
        'python': ['.py', '.pyw'],
        'javascript': ['.js', '.jsx', '.mjs'],
        'typescript': ['.ts', '.tsx'],
        'java': ['.java'],
        'go': ['.go'],
        'json': ['.json'],
        'xml': ['.xml', '.xsd', '.dtd'],
        'sql': ['.sql'],
        'bigquery': ['.bq', '.bqsql'],
        'dag': ['.py'],  # Airflow DAGs are Python files
    }
    
    # Framework detection patterns
    FRAMEWORK_PATTERNS = {
        'react': ['package.json'],
        'vue': ['package.json'],
        'angular': ['package.json', 'angular.json'],
        'django': ['manage.py', 'settings.py'],
        'flask': ['app.py', 'wsgi.py'],
        'spring': ['pom.xml', 'build.gradle'],
        'express': ['package.json'],
        'airflow': ['dags/', 'airflow.cfg'],
        'astronomer': ['Dockerfile', 'packages.txt'],
    }
    
    # Analysis rules
    ANALYSIS_RULES = {
        'max_function_length': 50,
        'max_cyclomatic_complexity': 10,
        'max_line_length': 120,
        'min_comment_ratio': 0.1,
    }
    
    @classmethod
    def load_custom_config(cls, config_path: str) -> None:
        """Load custom configuration from YAML file"""
        if not os.path.exists(config_path):
            return
        
        with open(config_path, 'r') as f:
            custom_config = yaml.safe_load(f)
        
        # Update configuration
        if 'server' in custom_config:
            cls.SERVER_HOST = custom_config['server'].get('host', cls.SERVER_HOST)
            cls.SERVER_PORT = custom_config['server'].get('port', cls.SERVER_PORT)
            cls.DEBUG = custom_config['server'].get('debug', cls.DEBUG)
        
        if 'analysis' in custom_config:
            cls.MAX_FILE_SIZE = custom_config['analysis'].get('max_file_size', cls.MAX_FILE_SIZE)
            cls.LARGE_REPO_THRESHOLD = custom_config['analysis'].get('large_repo_threshold', cls.LARGE_REPO_THRESHOLD)
        
        if 'rules' in custom_config:
            cls.ANALYSIS_RULES.update(custom_config['rules'])
    
    @classmethod
    def get_exclude_patterns(cls, additional_patterns: List[str] = None) -> List[str]:
        """Get combined exclude patterns"""
        patterns = cls.DEFAULT_EXCLUDE_PATTERNS.copy()
        if additional_patterns:
            patterns.extend(additional_patterns)
        return patterns
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'server': {
                'host': cls.SERVER_HOST,
                'port': cls.SERVER_PORT,
                'debug': cls.DEBUG,
            },
            'database': {
                'path': cls.DATABASE_PATH,
            },
            'analysis': {
                'max_file_size': cls.MAX_FILE_SIZE,
                'large_repo_threshold': cls.LARGE_REPO_THRESHOLD,
                'exclude_patterns': cls.DEFAULT_EXCLUDE_PATTERNS,
            },
            'severity_levels': cls.SEVERITY_LEVELS,
            'rules': cls.ANALYSIS_RULES,
        }
