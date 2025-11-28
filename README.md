# CodeReviewPro

> **Advanced AI-Powered Code Review & Quality Analysis for VS Code**

CodeReviewPro is a comprehensive code analysis tool that combines pattern-based detection with optional AI-powered insights to help you write better, more secure code.

## ✨ Key Features

- 🤖 **AI-Powered Analysis** - Optional LLM integration (OpenAI, Gemini, Claude, Perplexity, OpenRouter)
- 🌐 **Multi-Language Support** - Python, JavaScript/TypeScript, Java, Go, Rust, SQL, JSON
- 🛡️ **Security Scanning** - Detects OWASP Top 10 vulnerabilities and security issues
- 🐛 **Bug Detection** - Identifies common coding errors and anti-patterns
- ⚡ **Performance Analysis** - Flags inefficient code patterns
- 🎨 **VS Code Integration** - Seamless integration with Problems panel and WebView reports
- 📊 **Rich Reports** - Interactive HTML reports with tabbed severity views and filtering
- 📥 **Export Functionality** - Export reports to Excel, CSV, Word, PDF, Text, Markdown, HTML
- 🔄 **Smart Fallback** - Automatically falls back to pattern-based analysis when LLM unavailable
- 🔧 **Customizable** - Filter by category and severity

---

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Supported Languages](#supported-languages)
- [Usage](#usage)
- [AI-Powered Analysis](#ai-powered-analysis-optional)
- [Export Functionality](#export-functionality)
- [Configuration](#configuration)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## 🔧Installation

### Prerequisites

- **VS Code** 1.60.0 or higher
- **Python** 3.8 or higher
- **Node.js** 14.0 or higher (for extension development)

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Start the backend server
python server.py
```

The server will start on `http://localhost:5000`

### Extension Installation

#### Option 1: From VSIX (Recommended)
1. Open VS Code
2. Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac)
3. Type "Install from VSIX"
4. Select the `.vsix` file from the `extension` directory

#### Option 2: Development Mode
```bash
# Navigate to extension directory
cd extension

# Install dependencies
npm install

# Compile TypeScript
npm run compile

# Press F5 in VS Code to launch Extension Development Host
```

---

## 🚀Quick Start

### 1. Start the Backend Server

```bash
cd backend
python server.py
```

You should see:
```
INFO - Starting CodeReviewPro server on http://localhost:5000
```

### 2. Open Your Project in VS Code

Open any project containing supported language files.

### 3. Run a Scan

**Method 1: Command Palette**
- Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac)
- Type "CodeReviewPro: Scan Current Workspace"
- Press Enter

**Method 2: Status Bar**
- Click the "CodeReviewPro" button in the status bar

### 4. View Results

**Problems Panel:**
- Issues appear automatically in VS Code's Problems panel
- Click any issue to jump to the code

**WebView Report:**
- A detailed HTML report opens automatically
- **New in v1.2**: Tabbed view for Error, Warning, and Info severities
- Filter by category (Security, Bugs, Performance, Maintainability)
- Click the **Export Report** button to save in various formats

---

## 🌐Supported Languages

### Python (`.py`, `.pyw`)
- **Security**: Hardcoded secrets, eval/exec usage, bare except clauses
- **Bugs**: Type errors, undefined variables, mutable default arguments
- **Performance**: Inefficient loops, string concatenation in loops
- **Maintainability**: Function length, parameter count, code complexity

### JavaScript/TypeScript (`.js`, `.jsx`, `.ts`, `.tsx`, `.mjs`)
- **Security**: API keys, XSS vulnerabilities, dangerous functions
- **Bugs**: `==` vs `===`, console statements
- **Performance**: Multiple array iterations, inline functions
- **React**: Missing keys, useEffect dependencies, accessibility

### Java (`.java`)
- **Security**: Hardcoded credentials, SQL injection, unsafe deserialization
- **Bugs**: Empty catch blocks, string comparison with ==, potential NullPointerException
- **Performance**: String concatenation in loops, legacy collection usage
- **Maintainability**: Missing Javadoc, TODO comments

### Go (`.go`)
- **Security**: Hardcoded credentials, SQL injection, unsafe package usage
- **Bugs**: Unchecked errors, empty error checks
- **Performance**: String concatenation in loops
- **Maintainability**: Missing documentation for exported functions, TODO comments

### Rust (`.rs`)
- **Security**: Hardcoded credentials, unsafe blocks
- **Bugs**: unwrap() usage, direct indexing, empty expect() messages
- **Performance**: Cloning in loops, inefficient string operations
- **Maintainability**: Missing documentation for public functions, TODO comments

### SQL (`.sql`)
- **Performance**: SELECT *, missing indexes, missing WHERE clauses
- **Security**: SQL injection patterns
- **Best Practices**: Query optimization

### JSON (`.json`)
- **Validation**: Syntax errors, schema validation
- **Structure**: Deep nesting, large file warnings

---

## 📖Usage

### Basic Scan

```bash
# Scan current workspace
Ctrl+Shift+P → "CodeReviewPro: Scan Current Workspace"
```

### Configuration

Create `.vscode/settings.json` in your project:

```json
{
  "codereviewpro.serverUrl": "http://localhost:5000",
  "codereviewpro.excludePatterns": [
    "**/node_modules/**",
    "**/dist/**",
    "**/.git/**"
  ],
  "codereviewpro.severityLevels": {
    "security": "error",
    "bug": "error",
    "performance": "warning",
    "maintainability": "info"
  }
}
```

### Filtering Results

**In WebView Report:**
- **Tabbed View**: Switch between Error, Warning, and Info tabs
- **Category Filters**: Security, Bugs, Performance, Maintainability
- Click checkboxes to show/hide issues

**In Problems Panel:**
- Use VS Code's built-in filter (funnel icon)
- Filter by severity, file, or text

---

## 📥Export Functionality

### Export from WebView
- Click the **Export Report** button in the top-right corner of the report
- Select your desired format

### Export from Command Palette
- Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac)
- Run `CodeReviewPro: Export Report`
- Select format and save location

### Supported Export Formats

| Format | Extension | Description |
|--------|-----------|-------------|
| **Excel** | `.xlsx` | Tabular data with formatted columns |
| **CSV** | `.csv` | Comma-separated values for data analysis |
| **Word** | `.docx` | Formatted document with color-coded severity |
| **PDF** | `.pdf` | Professional report layout |
| **Text** | `.txt` | Plain text summary |
| **Markdown** | `.md` | Markdown formatted report |
| **HTML** | `.html` | Web-based report |

---

## 🤖AI-Powered Analysis (Optional)

CodeReviewPro v1.2 supports optional LLM integration for more intelligent, context-aware code reviews.

### Supported Providers

- **OpenAI**
- **Google Gemini**
- **Anthropic**
- **Perplexity**
- **OpenRouter**

### Setup

1. **Copy the example config:**
   ```bash
   cd backend
   cp llm_config.example.yaml llm_config.yaml
   ```

2. **Edit `llm_config.yaml` and configure your provider:**
   ```yaml
   llm:
     enabled: true
     provider: openai  # or gemini, anthropic, perplexity, openrouter
     
     openai:
       api_key: "your-api-key-here"  # Or use ${OPENAI_API_KEY}
       model: gpt-4
       max_tokens: 2000
       temperature: 0.3
   ```

3. **Restart the backend server:**
   ```bash
   python server.py
   ```

### How It Works

- **LLM-First Strategy**: When enabled, CodeReviewPro tries LLM analysis first
- **Smart Fallback**: If LLM is unavailable or credits exhausted, automatically falls back to pattern-based analysis
- **Same Reporting**: Results are displayed the same way regardless of analysis method
- **Rate Limiting**: Built-in rate limiting to avoid hitting API limits

### Cost Considerations

> [!WARNING]
> LLM-based analysis incurs API costs from your chosen provider. The system will automatically fallback to free pattern-based analysis when:
> - LLM is disabled in config
> - API key is invalid or missing
> - Rate limits are exceeded
> - API credits are exhausted

---

## ⚙️Configuration

### Server Configuration

Edit `backend/config.py`:

```python
class Config:
    # Server settings
    HOST = '0.0.0.0'
    PORT = 5000
    
    # File scanning
    MAX_FILE_SIZE = 1024 * 1024  # 1MB
    EXCLUDED_DIRS = ['.git', 'node_modules', '__pycache__', 'venv']
    
    # Supported extensions
    LANGUAGE_EXTENSIONS = {
        'python': ['.py', '.pyw'],
        'javascript': ['.js', '.jsx', '.mjs'],
        'typescript': ['.ts', '.tsx'],
        'java': ['.java'],
        'go': ['.go'],
        'rust': ['.rs'],
        'sql': ['.sql'],
        'json': ['.json']
    }
```

### Extension Configuration

Available settings in VS Code:

| Setting | Default | Description |
|---------|---------|-------------|
| `codereviewpro.serverUrl` | `http://localhost:5000` | Backend server URL |
| `codereviewpro.excludePatterns` | `["**/node_modules/**"]` | Files/folders to exclude |
| `codereviewpro.severityLevels` | See above | Severity mapping for categories |

---

## 🏗️Architecture

```
CodeReviewPro/
├── backend/                    # Python backend server
│   ├── analyzers/             # Code analyzers
│   │   ├── base_analyzer.py   # Base analyzer interface
│   │   ├── python_analyzer.py # Python analysis
│   │   ├── javascript_analyzer.py # JS/TS/React analysis
│   │   ├── java_analyzer.py   # Java analysis
│   │   ├── go_analyzer.py     # Go analysis
│   │   ├── rust_analyzer.py   # Rust analysis
│   │   ├── sql_analyzer.py    # SQL analysis
│   │   ├── json_analyzer.py   # JSON analysis
│   │   └── llm_analyzer.py    # AI-powered analysis
│   ├── llm_providers/         # LLM provider integrations
│   ├── exporters.py           # Report export functionality
│   ├── scanner.py             # Fast scanner (in-memory)
│   ├── server.py              # Flask REST API
│   ├── config.py              # Configuration
│   ├── utils.py               # Utilities
│   └── requirements.txt       # Python dependencies
│
└── extension/                  # VS Code extension
    ├── src/
    │   ├── extension.ts       # Main extension logic
    │   ├── serverClient.ts    # Backend communication
    │   ├── diagnosticProvider.ts # Problems panel integration
    │   ├── reportView.ts      # WebView report with export button
    │   └── types.ts           # TypeScript types
    ├── package.json           # Extension manifest
    └── tsconfig.json          # TypeScript config
```

### How It Works

1. **Extension** sends scan request to backend via REST API
2. **Backend** uses `os.walk()` for fast file collection
3. **Analyzers** process files in parallel (LLM-first, then pattern-based)
4. **Results** returned as JSON with camelCase field names
5. **Extension** displays issues in Problems panel and WebView

### Performance

- **File Collection**: `os.walk()` (100x faster than `rglob()` on Windows)
- **Analysis**: Parallel processing with pattern matching
- **Storage**: In-memory (no database overhead)
- **Speed**: 30+ files/second, 100 files in ~3-4 seconds

---

## 👨‍💻Development

### Backend Development

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run server in development mode
python server.py

# The server auto-reloads on code changes
```

### Extension Development

```bash
cd extension

# Install dependencies
npm install

# Compile TypeScript
npm run compile

# Watch mode (auto-compile on changes)
npm run watch

# Launch Extension Development Host
# Press F5 in VS Code
```

### Adding a New Analyzer

1. Create `backend/analyzers/your_analyzer.py`:

```python
from analyzers.base_analyzer import BaseAnalyzer, Issue, IssueCategory, IssueSeverity

class YourAnalyzer(BaseAnalyzer):
    def get_supported_extensions(self):
        return ['.ext']
    
    def analyze_file(self, file_path, content):
        issues = []
        # Your analysis logic
        return issues
```

2. Register in `backend/analyzers/__init__.py`:

```python
from .your_analyzer import YourAnalyzer

class AnalyzerRegistry:
    _analyzers = [
        LLMAnalyzer,
        YourAnalyzer,  # Add here
        # ... other analyzers
    ]
```

---

## 🐛Troubleshooting

### Backend Server Won't Start

**Problem**: `Address already in use`

**Solution**:
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :5000
kill -9 <PID>
```

### Extension Can't Connect to Backend

**Problem**: "Failed to connect to server"

**Solution**:
1. Verify server is running: `curl http://localhost:5000/health`
2. Check firewall settings
3. Verify `codereviewpro.serverUrl` in settings

### Scan Takes Too Long

**Problem**: Scan hangs or takes minutes

**Solution**:
1. Add exclusion patterns for large directories:
   ```json
   {
     "codereviewpro.excludePatterns": [
       "**/node_modules/**",
       "**/dist/**",
       "**/build/**",
       "**/.git/**"
     ]
   }
   ```

2. Check file count:
   ```bash
   # Should be < 1000 files
   find . -type f \( -name "*.py" -o -name "*.js" \) | wc -l
   ```

### Export Fails

**Problem**: Export button doesn't work or export fails

**Solution**:
1. Ensure backend dependencies are installed: `pip install -r requirements.txt`
2. Check that pandas, openpyxl, python-docx, and reportlab are installed
3. Restart the backend server

---

## 📊Example Output

### Console Output
```
INFO - Starting CodeReviewPro server on http://localhost:5000
INFO - Scanning 23 files
INFO - Scan completed: 30 issues in 23 files (0.8s)
```

### WebView Report
```
🔍 CodeReviewPro Report

📊 Overview
┌─────────┬────────┬───────────┬───────┐
│ New     │ Fixed  │ Remaining │ Total │
├─────────┼────────┼───────────┼───────┤
│ 30      │ 0      │ 0         │ 30    │
└─────────┴────────┴───────────┴───────┘

🆕 New Issues

Category: Security ▼
  [ERROR] Hardcoded API key detected
  Line 15: API_KEY = "hardcoded-key-123"
  💡 Move secrets to environment variables
```

---

## 📄License

MIT License - see [LICENSE](LICENSE) file for details

---

## 🤝Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/codereviewpro/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/codereviewpro/discussions)
- **Email**: support@codereviewpro.com

---

## 🎯 Roadmap

- [x] Multi-language support (Python, JS/TS, Java, Go, Rust, SQL, JSON)
- [x] AI-powered analysis with multiple LLM providers
- [x] Export to multiple formats (Excel, CSV, Word, PDF, etc.)
- [x] Tabbed severity views in reports
- [ ] Custom rule configuration
- [ ] CI/CD integration
- [ ] Team collaboration features
- [ ] Historical trend analysis

---

**Made with ❤️ by the CodeReviewPro Team**
