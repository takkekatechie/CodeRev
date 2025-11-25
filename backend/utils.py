"""
Common utilities for CodeReviewPro
"""

import os
import hashlib
from pathlib import Path
from typing import List, Tuple
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(name)

def estimate_repository_size(repo_path: str, exclude_patterns: List[str] = None) -> Tuple[int, int]:
    """
    Estimate repository size
    Returns: (total_files, total_size_bytes)
    """
    total_files = 0
    total_size = 0
    
    repo_path = Path(repo_path)
    
    for file_path in repo_path.rglob('*'):
        if file_path.is_file():
            # Check if file should be excluded
            if exclude_patterns and should_exclude(str(file_path), exclude_patterns):
                continue
            
            total_files += 1
            try:
                total_size += file_path.stat().st_size
            except (OSError, PermissionError):
                pass
    
    return total_files, total_size

def should_exclude(file_path: str, exclude_patterns: List[str]) -> bool:
    """Check if a file should be excluded based on patterns"""
    from fnmatch import fnmatch
    
    file_path = Path(file_path).as_posix()
    
    for pattern in exclude_patterns:
        if fnmatch(file_path, pattern):
            return True
    
    return False

def get_file_extension(file_path: str) -> str:
    """Get file extension without the dot"""
    return Path(file_path).suffix.lstrip('.')

def read_file_safe(file_path: str, max_size: int = None) -> str:
    """
    Safely read a file with size limit
    Returns empty string if file is too large or cannot be read
    """
    try:
        file_path = Path(file_path)
        
        # Check size
        if max_size and file_path.stat().st_size > max_size:
            return ''
        
        # Try to read as text
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception:
        return ''

def get_relative_path(file_path: str, base_path: str) -> str:
    """Get relative path from base path"""
    try:
        return str(Path(file_path).relative_to(base_path))
    except ValueError:
        return str(file_path)

def hash_content(content: str) -> str:
    """Generate SHA256 hash of content"""
    return hashlib.sha256(content.encode()).hexdigest()

def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def get_line_range(content: str, line_number: int, context: int = 2) -> Tuple[int, int, str]:
    """
    Get a range of lines around a specific line number
    Returns: (start_line, end_line, snippet)
    """
    lines = content.split('\n')
    total_lines = len(lines)
    
    start = max(0, line_number - context - 1)
    end = min(total_lines, line_number + context)
    
    snippet = '\n'.join(lines[start:end])
    
    return start + 1, end, snippet

def is_binary_file(file_path: str) -> bool:
    """Check if a file is binary"""
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(1024)
            return b'\x00' in chunk
    except Exception:
        return True

def count_lines(file_path: str) -> int:
    """Count lines in a file"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return sum(1 for _ in f)
    except Exception:
        return 0

class ProgressTracker:
    """Simple progress tracker"""
    
    def __init__(self, total: int):
        self.total = total
        self.current = 0
        self.logger = get_logger('ProgressTracker')
    
    def update(self, increment: int = 1, message: str = None) -> float:
        """Update progress and return percentage"""
        self.current += increment
        percentage = (self.current / self.total * 100) if self.total > 0 else 0
        
        if message:
            self.logger.info(f"{message} ({percentage:.1f}%)")
        
        return percentage
    
    def get_percentage(self) -> float:
        """Get current percentage"""
        return (self.current / self.total * 100) if self.total > 0 else 0
