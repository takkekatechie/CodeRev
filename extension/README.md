# CodeReviewPro VS Code Extension

Advanced peer review and code quality assessment extension for Visual Studio Code.

## Features

- 🔍 **Comprehensive Code Analysis**: Analyzes Python, JavaScript/TypeScript, Java, Go, SQL, JSON, XML, BigQuery, and Airflow DAGs
- 🛡️ **Security Scanning**: Detects OWASP Top 10 vulnerabilities and security issues
- 📊 **Rich Reports**: Interactive WebView reports with tabbed severity views, filtering, and categorization
- 🔄 **Scan Comparison**: Track progress by comparing scans over time
- 💡 **Actionable Recommendations**: Get specific, ready-to-implement fix suggestions
- ⚡ **Real-time Diagnostics**: Issues appear directly in VS Code's Problems panel

## Installation

### Prerequisites

1. **Backend Server**: The extension requires the CodeReviewPro backend server to be running
2. **Python 3.8+**: Required for the backend server

### Steps

1. Install the extension from the VS Code Marketplace
2. Start the backend server:
   ```bash
   cd backend
   pip install -r requirements.txt
   python server.py
   ```
3. Configure the server URL in VS Code settings (default: `http://localhost:5000`)

## Usage

### Scanning Your Workspace

1. Open Command Palette (`Ctrl+Shift+P` or `Cmd+Shift+P`)
2. Run `CodeReviewPro: Scan Current Workspace`
3. Wait for the scan to complete
4. View results in the Problems panel and the new tabbed WebView report

### Viewing Reports

- **Latest Report**: Run `CodeReviewPro: View Last Report`
- **Compare Scans**: Run `CodeReviewPro: Compare Scans` to see Fixed/New/Remaining issues
- **Export Report**: Run `CodeReviewPro: Export Report` to save as Markdown, HTML, or PDF

### Configuration

Access settings via `CodeReviewPro: Configure Settings` or manually edit:

```json
{
  "codereviewpro.serverUrl": "http://localhost:5000",
  "codereviewpro.autoScanOnSave": false,
  "codereviewpro.severityLevels": {
    "security": "error",
    "bug": "error",
    "performance": "warning",
    "maintainability": "info",
    "architecture": "info"
  },
  "codereviewpro.excludePatterns": [
    "**/node_modules/**",
    "**/dist/**",
    "**/build/**"
  ],
  "codereviewpro.confirmLargeScan": true
}
```

## Supported Languages

- Python
- JavaScript/TypeScript
- Java
- Go
- SQL
- Google BigQuery
- JSON
- XML
- Airflow DAGs (Astronomer)

## Issue Categories

- **🛡️ Security**: OWASP Top 10, hardcoded secrets, injection vulnerabilities
- **🐛 Bugs**: Null references, logic errors, resource leaks
- **⚡ Performance**: Algorithmic complexity, inefficient operations
- **🔧 Maintainability**: Code complexity, style violations, duplication
- **🏗️ Architecture**: Design patterns, separation of concerns

## Development

### Building from Source

```bash
cd extension
npm install
npm run compile
```

### Running Tests

```bash
npm test
```

### Packaging

```bash
npm run package
```

## License

MIT

## Support

For issues and feature requests, please visit our [GitHub repository](https://github.com/codereviewpro/codereviewpro).
