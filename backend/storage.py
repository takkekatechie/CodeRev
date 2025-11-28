"""
Storage Manager for CodeReviewPro
Handles SQLite database interactions for persistent scan history and knowledge base.
"""

import sqlite3
import json
import os
import time
from typing import List, Dict, Any, Optional
from utils import get_logger

logger = get_logger(__name__)

class StorageManager:
    def __init__(self, db_path: str = 'codereview.db'):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        """Initialize database tables"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Scans table
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS scans (
                    id TEXT PRIMARY KEY,
                    timestamp REAL,
                    repo_path TEXT,
                    version TEXT,
                    status TEXT,
                    summary TEXT,
                    total_files INTEGER,
                    languages TEXT,
                    error TEXT
                )
                ''')
                
                # Issues table (linked to scans)
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS scan_issues (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_id TEXT,
                    file_path TEXT,
                    category TEXT,
                    severity TEXT,
                    line_start INTEGER,
                    line_end INTEGER,
                    description TEXT,
                    recommendation TEXT,
                    FOREIGN KEY(scan_id) REFERENCES scans(id)
                )
                ''')
                
                # Knowledge Base (Learned Patterns)
                # Maps file content hash to discovered issues
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS knowledge_base (
                    file_hash TEXT PRIMARY KEY,
                    issues_json TEXT,
                    timestamp REAL,
                    source TEXT
                )
                ''')
                
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")

    def save_scan(self, scan_data: Dict[str, Any]):
        """Save a complete scan result"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Insert scan metadata
                cursor.execute('''
                INSERT OR REPLACE INTO scans 
                (id, timestamp, repo_path, version, status, summary, total_files, languages, error)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    scan_data['scan_id'],
                    scan_data.get('end_time', time.time()),
                    scan_data['repo_path'],
                    scan_data.get('version', '1.2.0'),
                    scan_data['status'],
                    json.dumps(scan_data.get('summary', {})),
                    scan_data.get('total_files', 0),
                    json.dumps(scan_data.get('languages', [])),
                    scan_data.get('error', '')
                ))
                
                # Insert issues
                # First delete existing issues for this scan (if update)
                cursor.execute('DELETE FROM scan_issues WHERE scan_id = ?', (scan_data['scan_id'],))
                
                issues = scan_data.get('issues', [])
                for issue in issues:
                    cursor.execute('''
                    INSERT INTO scan_issues 
                    (scan_id, file_path, category, severity, line_start, line_end, description, recommendation)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        scan_data['scan_id'],
                        issue.get('filePath', ''),
                        issue.get('category', ''),
                        issue.get('severity', ''),
                        issue.get('lineStart', 0),
                        issue.get('lineEnd', 0),
                        issue.get('description', ''),
                        issue.get('recommendation', '')
                    ))
                
                conn.commit()
                logger.info(f"Saved scan {scan_data['scan_id']} to database")
        except Exception as e:
            logger.error(f"Failed to save scan: {e}")

    def get_scan(self, scan_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific scan"""
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('SELECT * FROM scans WHERE id = ?', (scan_id,))
                row = cursor.fetchone()
                
                if not row:
                    return None
                
                scan = dict(row)
                # Parse JSON fields
                scan['languages'] = json.loads(scan['languages']) if scan['languages'] else []
                scan['summary'] = json.loads(scan['summary']) if scan['summary'] else {}
                
                # Get issues
                cursor.execute('SELECT * FROM scan_issues WHERE scan_id = ?', (scan_id,))
                issues_rows = cursor.fetchall()
                issues = []
                for i_row in issues_rows:
                    issue = dict(i_row)
                    # Remap keys to match frontend expectation
                    issues.append({
                        'filePath': issue['file_path'],
                        'category': issue['category'],
                        'severity': issue['severity'],
                        'lineStart': issue['line_start'],
                        'lineEnd': issue['line_end'],
                        'description': issue['description'],
                        'recommendation': issue['recommendation']
                    })
                
                scan['issues'] = issues
                return scan
        except Exception as e:
            logger.error(f"Failed to get scan {scan_id}: {e}")
            return None

    def get_history(self, repo_path: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get scan history, optionally filtered by repo"""
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                query = 'SELECT * FROM scans'
                params = []
                
                if repo_path:
                    query += ' WHERE repo_path = ?'
                    params.append(repo_path)
                
                query += ' ORDER BY timestamp DESC LIMIT ?'
                params.append(limit)
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                history = []
                for row in rows:
                    scan = dict(row)
                    scan['languages'] = json.loads(scan['languages']) if scan['languages'] else []
                    scan['summary'] = json.loads(scan['summary']) if scan['summary'] else {}
                    
                    # Map timestamp to scanDate for frontend
                    if scan.get('timestamp'):
                        from datetime import datetime
                        scan['scanDate'] = datetime.fromtimestamp(scan['timestamp']).isoformat()
                        
                    # Don't load issues for list view to keep it light
                    history.append(scan)
                
                return history
        except Exception as e:
            logger.error(f"Failed to get history: {e}")
            return []

    def save_knowledge(self, file_hash: str, issues: List[Dict[str, Any]], source: str = 'llm'):
        """Catalog findings for a specific file content hash"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                INSERT OR REPLACE INTO knowledge_base (file_hash, issues_json, timestamp, source)
                VALUES (?, ?, ?, ?)
                ''', (
                    file_hash,
                    json.dumps(issues),
                    time.time(),
                    source
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to save knowledge: {e}")

    def get_knowledge(self, file_hash: str) -> Optional[List[Dict[str, Any]]]:
        """Retrieve cataloged findings for a file hash"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT issues_json FROM knowledge_base WHERE file_hash = ?', (file_hash,))
                row = cursor.fetchone()
                
                if row:
                    return json.loads(row[0])
                return None
        except Exception as e:
            logger.error(f"Failed to get knowledge: {e}")
            return None
