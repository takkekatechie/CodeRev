# CodeReviewPro VS Code Extension

> **Advanced AI-Powered Code Review & Quality Analysis**

Professional code analysis extension for Visual Studio Code with AI-powered insights and comprehensive multi-language support.

## ✨ Features

- 🔍 **Comprehensive Code Analysis**: Analyzes Python, JavaScript/TypeScript, Java, Go, Rust, SQL, and JSON
- 🛡️ **Security Scanning**: Detects OWASP Top 10 vulnerabilities and security issues
- 📊 **Rich Reports**: Interactive WebView reports with tabbed severity views, filtering, and categorization
- 📥 **Export Functionality**: Export reports to Excel, CSV, Word, PDF, Text, Markdown, and HTML
- 🔄 **Scan Comparison**: Track progress by comparing scans over time
- 💡 **Actionable Recommendations**: Get specific, ready-to-implement fix suggestions
- ⚡ **Real-time Diagnostics**: Issues appear directly in VS Code's Problems panel
- 🤖 **AI-Powered Analysis**: Optional LLM integration for intelligent code reviews

## 🔧 Installation

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

## 🚀 Usage

### Scanning Your Workspace

1. Open Command Palette (`Ctrl+Shift+P` or `Cmd+Shift+P`)
2. Run `CodeReviewPro: Scan Current Workspace`
3. Wait for the scan to complete
4. View results in the Problems panel and the new tabbed WebView report

### Viewing Reports

- **Latest Report**: Run `CodeReviewPro: View Last Report`
- **Compare Scans**: Run `CodeReviewPro: Compare Scans` to see Fixed/New/Remaining issues
- **Export Report**: Click the export button in the report or run `CodeReviewPro: Export Report`

### Exporting Reports

**From WebView:**
- Click the **Export Report** button in the top-right corner of the report
- Select your desired format (Excel, CSV, Word, PDF, Text, Markdown, HTML)

**From Command Palette:**
- Run `CodeReviewPro: Export Report`
- Select format and save location

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

## 🤖 AI-Powered Analysis

CodeReviewPro supports optional LLM integration for more intelligent, context-aware code reviews.

### Supported Providers

- **OpenAI** (GPT-4, GPT-3.5-turbo)
- **Google Gemini** (Gemini Pro, Gemini 1.5 Pro)
- **Anthropic** (Claude-3 Opus, Sonnet, Haiku)
- **Perplexity** (pplx-70b-online)
- **OpenRouter** (Access to multiple models)

### Setup

Configure your LLM provider in `backend/llm_config.yaml` and restart the backend server.

## 🌐 Supported Languages

### Python (`.py`, `.pyw`)
- Security, bugs, performance, maintainability checks
- AST-based analysis for deep code understanding

### JavaScript/TypeScript (`.js`, `.jsx`, `.ts`, `.tsx`, `.mjs`)
- React-specific checks (hooks, keys, accessibility)
- Modern JavaScript patterns and anti-patterns

### Java (`.java`)
- Security vulnerabilities (SQL injection, deserialization)
- Common bugs (NullPointerException, string comparison)
- Performance optimizations

### Go (`.go`)
- Error handling patterns
- Concurrency issues
- Performance optimizations

### Rust (`.rs`)
- Unsafe code detection
- Ownership and borrowing issues
- Performance patterns

### SQL (`.sql`)
- Injection vulnerabilities
- Query optimization
- Best practices

### JSON (`.json`)
- Schema validation
- Structure analysis

## 📊 Issue Categories

- **🛡️ Security**: OWASP Top 10, hardcoded secrets, injection vulnerabilities
- **🐛 Bugs**: Null references, logic errors, resource leaks
- **⚡ Performance**: Algorithmic complexity, inefficient operations
- **🔧 Maintainability**: Code complexity, style violations, duplication
- **🏗️ Architecture**: Design patterns, separation of concerns

## 🎨 Report Features

### Tabbed Severity View (v1.2)
- **Errors Tab**: Critical issues requiring immediate attention
- **Warnings Tab**: Important issues to address
- **Info Tab**: Suggestions and best practices

### Filtering
- Filter by category (Security, Bugs, Performance, etc.)
- Filter by severity (Error, Warning, Info)
- Search within issues

### Export Options
- **Excel** (`.xlsx`) - Tabular data with formatted columns
- **CSV** (`.csv`) - For data analysis and reporting
- **Word** (`.docx`) - Formatted document with color-coded severity
- **PDF** (`.pdf`) - Professional report layout
- **Text** (`.txt`) - Plain text summary
- **Markdown** (`.md`) - Markdown formatted report
- **HTML** (`.html`) - Web-based report

## 👨‍💻 Development

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

## 🔧 Commands

| Command | Description |
|---------|-------------|
| `CodeReviewPro: Scan Current Workspace` | Scan all files in the workspace |
| `CodeReviewPro: View Last Report` | View the most recent scan report |
| `CodeReviewPro: Compare Scans` | Compare two scans to see progress |
| `CodeReviewPro: Export Report` | Export the current report |
| `CodeReviewPro: Configure Settings` | Open extension settings |

## ⚙️ Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `codereviewpro.serverUrl` | string | `http://localhost:5000` | Backend server URL |
| `codereviewpro.autoScanOnSave` | boolean | `false` | Automatically scan on file save |
| `codereviewpro.excludePatterns` | array | `["**/node_modules/**"]` | File patterns to exclude |
| `codereviewpro.confirmLargeScan` | boolean | `true` | Confirm before scanning large repos |
| `codereviewpro.severityLevels` | object | See above | Severity mapping for categories |

## 🐛 Troubleshooting

### Backend Not Running
- Ensure the backend server is started: `python backend/server.py`
- Check the server URL in settings matches the running server

### No Issues Found
- Verify supported file types exist in workspace
- Check exclusion patterns aren't too broad
- Review analyzer logs in backend console

### Export Not Working
- Ensure all backend dependencies are installed
- Restart the backend server after installing new dependencies
- Check console for error messages

## 📄 License

MIT

## 🤝 Support

For issues and feature requests, please visit our [GitHub repository](https://github.com/codereviewpro/codereviewpro).

---

**Version 1.2.0** - Now with tabbed reports, export functionality, and support for Go, Rust, and Java!
