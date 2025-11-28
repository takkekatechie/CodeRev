"""
Simple in-memory cache for LLM responses
"""

import hashlib
import time
from typing import Optional, List, Dict, Any


class LLMCache:
    """In-memory cache for LLM analysis results"""
    
    def __init__(self, ttl_seconds: int = 3600):
        """
        Initialize cache
        
        Args:
            ttl_seconds: Time to live for cache entries (default 1 hour)
        """
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = ttl_seconds
    
    def _hash_content(self, content: str) -> str:
        """Generate hash for file content"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def get(self, file_path: str, content: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get cached analysis result
        
        Args:
            file_path: Path to the file
            content: File content
        
        Returns:
            Cached issues or None if not found/expired
        """
        content_hash = self._hash_content(content)
        cache_key = f"{file_path}:{content_hash}"
        
        if cache_key in self.cache:
            entry = self.cache[cache_key]
            
            # Check if expired
            if time.time() - entry['timestamp'] < self.ttl:
                return entry['issues']
            else:
                # Remove expired entry
                del self.cache[cache_key]
        
        return None
    
    def set(self, file_path: str, content: str, issues: List[Dict[str, Any]]):
        """
        Cache analysis result
        
        Args:
            file_path: Path to the file
            content: File content
            issues: Analysis issues to cache
        """
        content_hash = self._hash_content(content)
        cache_key = f"{file_path}:{content_hash}"
        
        self.cache[cache_key] = {
            'issues': issues,
            'timestamp': time.time()
        }
    
    def clear(self):
        """Clear all cache entries"""
        self.cache.clear()
    
    def cleanup_expired(self):
        """Remove expired cache entries"""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self.cache.items()
            if current_time - entry['timestamp'] >= self.ttl
        ]
        
        for key in expired_keys:
            del self.cache[key]
    
    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        return {
            'total_entries': len(self.cache),
            'ttl_seconds': self.ttl
        }
