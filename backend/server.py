"""
Flask REST API server for CodeReviewPro
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import os

from scanner import ScanOrchestrator
from utils import get_logger

logger = get_logger(__name__)

app = Flask(__name__)
CORS(app)

# Single scanner instance
scanner = ScanOrchestrator()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'version': '1.0.0'}), 200

@app.route('/api/scan', methods=['POST'])
def start_scan():
    try:
        data = request.get_json()
        
        if not data or 'repositoryPath' not in data:
            return jsonify({'error': 'repositoryPath is required'}), 400
        
        repo_path = data['repositoryPath']
        
        if not os.path.exists(repo_path):
            return jsonify({'error': 'Repository path does not exist'}), 404
        
        if not os.path.isdir(repo_path):
            return jsonify({'error': 'Repository path must be a directory'}), 400
        
        exclude_patterns = data.get('excludePatterns', [])
        
        # Start scan (synchronous now, but fast)
        scan_id = scanner.start_scan(repo_path, exclude_patterns)
        
        return jsonify({
            'scanId': scan_id,
            'status': 'started',
            'message': 'Scan started successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error starting scan: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/scan/<scan_id>/status', methods=['GET'])
def get_scan_status(scan_id):
    try:
        status = scanner.get_scan_status(scan_id)
        return jsonify(status), 200
    except Exception as e:
        logger.error(f"Error getting status: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/scan/<scan_id>/results', methods=['GET'])
def get_scan_results(scan_id):
    try:
        results = scanner.get_scan_results(scan_id)
        
        if 'error' in results:
            return jsonify(results), 404 if results['error'] == 'Scan not found' else 400
        
        return jsonify(results), 200
    except Exception as e:
        logger.error(f"Error getting results: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/scan/compare', methods=['POST'])
def compare_scans():
    # Simplified - just return current scan for now
    try:
        data = request.get_json()
        current_scan_id = data.get('current_scan_id')
        
        if not current_scan_id:
            return jsonify({'error': 'current_scan_id required'}), 400
        
        results = scanner.get_scan_results(current_scan_id)
        
        if 'error' in results:
            return jsonify(results), 404
        
        # Simple comparison - all issues are "new" for now
        return jsonify({
            'currentScan': results,
            'previousScan': None,
            'newIssues': results['issues'],
            'fixedIssues': [],
            'remainingIssues': [],
        }), 200
        
    except Exception as e:
        logger.error(f"Error comparing: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

def main():
    logger.info("Starting CodeReviewPro server on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == '__main__':
    main()
