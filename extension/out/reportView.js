"use strict";
/**
 * WebView-based report viewer for CodeReviewPro
 */
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.ReportView = void 0;
const vscode = __importStar(require("vscode"));
class ReportView {
    constructor(extensionUri) {
        this.extensionUri = extensionUri;
    }
    /**
     * Show the report view
     */
    show(result) {
        if (this.panel) {
            this.panel.reveal(vscode.ViewColumn.One);
        }
        else {
            this.panel = vscode.window.createWebviewPanel('codereviewproReport', 'CodeReviewPro Report', vscode.ViewColumn.One, {
                enableScripts: true,
                retainContextWhenHidden: true,
            });
            this.panel.onDidDispose(() => {
                this.panel = undefined;
            });
        }
        this.panel.webview.html = this.getHtmlContent(result);
    }
    getHtmlContent(result) {
        const { currentScan, previousScan, newIssues, fixedIssues, remainingIssues } = result;
        return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CodeReviewPro Report</title>
  <style>
    ${this.getStyles()}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>🔍 CodeReviewPro Report</h1>
      <div class="metadata">
        <p><strong>Scan Date:</strong> ${currentScan.scanDate ? new Date(currentScan.scanDate).toLocaleString() : new Date().toLocaleString()}</p>
        <p><strong>Repository:</strong> ${currentScan.repositoryPath || 'Unknown'}</p>
      </div>
    </header>

    <section class="environment">
      <h2>🛠️ Environment</h2>
      <ul>
        <li><strong>Languages:</strong> ${(currentScan.detectedLanguages || []).join(', ') || 'Unknown'}</li>
        <li><strong>Frameworks:</strong> ${(currentScan.detectedFrameworks || []).join(', ') || 'None'}</li>
        <li><strong>Files:</strong> ${currentScan.totalFiles || 0}</li>
      </ul>
    </section>

    <section class="summary">
      <h2>📊 Overview</h2>
      <div class="summary-grid">
        <div class="summary-card new">
          <div class="card-value">${newIssues.length}</div>
          <div class="card-label">New</div>
        </div>
        <div class="summary-card fixed">
          <div class="card-value">${fixedIssues.length}</div>
          <div class="card-label">Fixed</div>
        </div>
        <div class="summary-card remaining">
          <div class="card-value">${remainingIssues.length}</div>
          <div class="card-label">Remaining</div>
        </div>
        <div class="summary-card total">
          <div class="card-value">${currentScan.summary.totalIssues}</div>
          <div class="card-label">Total</div>
        </div>
      </div>
    </section>

    <div class="tabs">
      <button class="tab-btn active" data-tab="error">
        <span class="tab-icon">🔴</span> Errors
        <span class="tab-count">${this.countBySeverity(newIssues.concat(remainingIssues), 'error')}</span>
      </button>
      <button class="tab-btn" data-tab="warning">
        <span class="tab-icon">🟡</span> Warnings
        <span class="tab-count">${this.countBySeverity(newIssues.concat(remainingIssues), 'warning')}</span>
      </button>
      <button class="tab-btn" data-tab="info">
        <span class="tab-icon">🔵</span> Info
        <span class="tab-count">${this.countBySeverity(newIssues.concat(remainingIssues), 'info')}</span>
      </button>
    </div>

    <div id="error-content" class="tab-content active">
      ${this.renderIssuesBySeverity(newIssues.concat(remainingIssues), 'error')}
    </div>
    <div id="warning-content" class="tab-content">
      ${this.renderIssuesBySeverity(newIssues.concat(remainingIssues), 'warning')}
    </div>
    <div id="info-content" class="tab-content">
      ${this.renderIssuesBySeverity(newIssues.concat(remainingIssues), 'info')}
    </div>

  </div>

  <script>
    ${this.getScripts()}
  </script>
</body>
</html>`;
    }
    countBySeverity(issues, severity) {
        return issues.filter(i => i.severity.toLowerCase() === severity.toLowerCase()).length;
    }
    renderIssuesBySeverity(issues, severity) {
        const filteredIssues = issues.filter(i => i.severity.toLowerCase() === severity.toLowerCase());
        if (filteredIssues.length === 0) {
            return `<div class="no-issues">
        <p>No ${severity}s found. Great job! 🎉</p>
      </div>`;
        }
        const issuesByCategory = this.groupByCategory(filteredIssues);
        let html = '';
        for (const [category, catIssues] of Object.entries(issuesByCategory)) {
            html += `<div class="cat-section">
          <h3 class="cat-header ${category}">${this.getCategoryIcon(category)} ${this.capitalize(category)}</h3>
          <div class="issues-list">
            ${catIssues.map(issue => this.renderIssue(issue)).join('')}
          </div>
        </div>`;
        }
        return html;
    }
    // Kept for backward compatibility if needed, but not used in new layout
    renderIssueSection(title, issues) {
        return '';
    }
    renderIssue(issue) {
        return `<div class="issue-card ${issue.severity}" data-sev="${issue.severity}">
        <div class="issue-header">
          <span class="severity-badge ${issue.severity}">${issue.severity.toUpperCase()}</span>
          <span class="file-path">${this.getRelativePath(issue.filePath)}</span>
          <span class="line-number">Lines ${issue.lineStart}-${issue.lineEnd}</span>
        </div>
        <div class="issue-description">${issue.description}</div>
        ${issue.recommendation ? `<div class="issue-recommendation"><strong>💡 Recommendation:</strong> ${issue.recommendation}</div>` : ''}
      </div>`;
    }
    groupByCategory(issues) {
        const grouped = {};
        for (const issue of issues) {
            if (!grouped[issue.category]) {
                grouped[issue.category] = [];
            }
            grouped[issue.category].push(issue);
        }
        return grouped;
    }
    getCategoryIcon(category) {
        const icons = {
            security: '🛡️',
            bug: '🐛',
            performance: '⚡',
            maintainability: '🔧',
            architecture: '🏗️',
        };
        return icons[category] || '📌';
    }
    capitalize(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }
    getRelativePath(filePath) {
        const parts = filePath.split(/[\\/]/);
        return parts.slice(-3).join('/');
    }
    getStyles() {
        return `
      * { margin: 0; padding: 0; box-sizing: border-box; }
      body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        line-height: 1.6;
        color: var(--vscode-foreground);
        background: var(--vscode-editor-background);
        padding: 20px;
      }
      .container { max-width: 1200px; margin: 0 auto; }
      header { margin-bottom: 30px; padding-bottom: 20px; border-bottom: 2px solid var(--vscode-panel-border); }
      h1 { font-size: 2em; margin-bottom: 10px; }
      h2 { font-size: 1.5em; margin: 20px 0 15px; }
      h3 { font-size: 1.2em; margin: 15px 0 10px; }
      .metadata p { margin: 5px 0; color: var(--vscode-descriptionForeground); }
      .environment ul { list-style: none; padding: 15px; background: var(--vscode-editor-inactiveSelectionBackground); border-radius: 5px; }
      .environment li { margin: 8px 0; }
      .summary-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }
      .summary-card { padding: 20px; border-radius: 8px; text-align: center; border: 2px solid; }
      .summary-card.new { border-color: #f59e0b; background: rgba(245, 158, 11, 0.1); }
      .summary-card.fixed { border-color: #10b981; background: rgba(16, 185, 129, 0.1); }
      .summary-card.remaining { border-color: #ef4444; background: rgba(239, 68, 68, 0.1); }
      .summary-card.total { border-color: #3b82f6; background: rgba(59, 130, 246, 0.1); }
      .card-value { font-size: 2.5em; font-weight: bold; margin-bottom: 5px; }
      .card-label { font-size: 0.9em; opacity: 0.8; }
      
      /* Tabs */
      .tabs { display: flex; gap: 10px; margin-bottom: 20px; border-bottom: 2px solid var(--vscode-panel-border); }
      .tab-btn {
        background: none;
        border: none;
        padding: 10px 20px;
        cursor: pointer;
        font-size: 1em;
        color: var(--vscode-foreground);
        opacity: 0.7;
        border-bottom: 3px solid transparent;
        transition: all 0.2s;
        display: flex;
        align-items: center;
        gap: 8px;
      }
      .tab-btn:hover { opacity: 1; background: var(--vscode-toolbar-hoverBackground); }
      .tab-btn.active { opacity: 1; border-bottom-color: var(--vscode-button-background); font-weight: bold; }
      .tab-count { background: var(--vscode-badge-background); color: var(--vscode-badge-foreground); padding: 2px 8px; border-radius: 10px; font-size: 0.8em; }
      .tab-content { display: none; }
      .tab-content.active { display: block; animation: fadeIn 0.3s ease; }
      
      @keyframes fadeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }

      .cat-section { margin: 20px 0; }
      .cat-header { padding: 10px; border-radius: 5px; margin-bottom: 10px; }
      .cat-header.security { background: rgba(239, 68, 68, 0.2); }
      .cat-header.bug { background: rgba(245, 158, 11, 0.2); }
      .cat-header.performance { background: rgba(59, 130, 246, 0.2); }
      .cat-header.maintainability { background: rgba(16, 185, 129, 0.2); }
      .issues-list { display: flex; flex-direction: column; gap: 15px; }
      .issue-card { padding: 15px; border-left: 4px solid; background: var(--vscode-editor-inactiveSelectionBackground); border-radius: 5px; }
      .issue-card.error { border-left-color: #ef4444; }
      .issue-card.warning { border-left-color: #f59e0b; }
      .issue-card.info { border-left-color: #3b82f6; }
      .issue-header { display: flex; gap: 10px; align-items: center; margin-bottom: 10px; flex-wrap: wrap; }
      .severity-badge { padding: 3px 8px; border-radius: 3px; font-size: 0.75em; font-weight: bold; }
      .severity-badge.error { background: #ef4444; color: white; }
      .severity-badge.warning { background: #f59e0b; color: white; }
      .severity-badge.info { background: #3b82f6; color: white; }
      .file-path { font-family: 'Courier New', monospace; font-size: 0.9em; opacity: 0.8; }
      .line-number { font-size: 0.85em; opacity: 0.7; }
      .issue-description { margin: 10px 0; line-height: 1.5; }
      .issue-recommendation { margin: 10px 0; padding: 10px; background: rgba(16, 185, 129, 0.1); border-left: 3px solid #10b981; border-radius: 3px; }
      .no-issues { padding: 40px; text-align: center; opacity: 0.7; font-size: 1.2em; background: var(--vscode-editor-inactiveSelectionBackground); border-radius: 8px; margin-top: 20px; }
    `;
    }
    getScripts() {
        return `
      // Tab switching logic
      document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          // Remove active class from all tabs and contents
          document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
          document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
          
          // Add active class to clicked tab
          btn.classList.add('active');
          
          // Show corresponding content
          const tabId = btn.dataset.tab;
          document.getElementById(tabId + '-content').classList.add('active');
        });
      });
    `;
    }
    dispose() {
        if (this.panel) {
            this.panel.dispose();
        }
    }
}
exports.ReportView = ReportView;
//# sourceMappingURL=reportView.js.map