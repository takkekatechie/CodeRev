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
    constructor(extensionUri, serverClient) {
        this.scanHistory = [];
        this.extensionUri = extensionUri;
        this.serverClient = serverClient;
    }
    /**
     * Show the report view
     */
    async show(result) {
        // Store the current scan ID and repository path
        this.currentScanId = result.currentScan.scanId;
        this.repositoryPath = result.currentScan.repositoryPath;
        // Load scan history
        if (this.serverClient && this.repositoryPath) {
            try {
                this.scanHistory = await this.serverClient.getScanHistory(this.repositoryPath);
            }
            catch (error) {
                console.error('Failed to load scan history:', error);
                this.scanHistory = [];
            }
        }
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
                this.currentScanId = undefined;
            });
            // Handle messages from webview
            this.panel.webview.onDidReceiveMessage(async (message) => {
                if (message.command === 'export') {
                    this.handleExport();
                }
                else if (message.command === 'loadScan') {
                    await this.handleLoadScan(message.scanId);
                }
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
      <div class="header-content">
        <div>
          <h1>🔍 CodeReviewPro Report</h1>
          <div class="metadata">
            <p><strong>Scan Date:</strong> ${currentScan.scanDate ? new Date(currentScan.scanDate).toLocaleString() : new Date().toLocaleString()}</p>
            <p><strong>Repository:</strong> ${currentScan.repositoryPath || 'Unknown'}</p>
            ${this.scanHistory.length > 1 ? `
            <div class="scan-selector">
              <label for="scan-history"><strong>View Past Scans:</strong></label>
              <select id="scan-history" onchange="loadSelectedScan(this.value)">
                ${this.scanHistory.filter(s => s && s.scanId).map(scan => {
            const dateStr = scan.scanDate ? new Date(scan.scanDate).toLocaleString() : 'Unknown Date';
            const issueCount = scan.summary?.totalIssues !== undefined ? scan.summary.totalIssues : (scan.issues?.length || 0);
            return `<option value="${scan.scanId}" ${scan.scanId === currentScan.scanId ? 'selected' : ''}>
                    ${dateStr} - ${issueCount} issues
                  </option>`;
        }).join('')}
              </select>
            </div>
            ` : ''}
          </div>
        </div>
        <button class="export-btn" onclick="exportReport()">
          <span class="export-icon">📥</span> Export Report
        </button>
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
          <h3 class="cat-header ${category}" onclick="toggleCategory(this)">
            <span class="cat-title">
              ${this.getCategoryIcon(category)} ${this.capitalize(category)}
              <span class="cat-count">(${catIssues.length})</span>
            </span>
            <span class="chevron">▼</span>
          </h3>
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
      .header-content { display: flex; justify-content: space-between; align-items: flex-start; gap: 20px; }
      .scan-selector { margin-top: 10px; }
      .scan-selector label { display: block; margin-bottom: 5px; font-size: 0.9em; }
      .scan-selector select {
        width: 100%;
        padding: 8px;
        border: 1px solid var(--vscode-input-border);
        background: var(--vscode-input-background);
        color: var(--vscode-input-foreground);
        border-radius: 3px;
        font-size: 0.9em;
        cursor: pointer;
      }
      .scan-selector select:hover { border-color: var(--vscode-focusBorder); }
      .scan-selector select:focus { outline: 1px solid var(--vscode-focusBorder); }
      .export-btn {
        background: var(--vscode-button-background);
        color: var(--vscode-button-foreground);
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        cursor: pointer;
        font-size: 0.9em;
        display: flex;
        align-items: center;
        gap: 8px;
        transition: background 0.2s;
        white-space: nowrap;
      }
      .export-btn:hover { background: var(--vscode-button-hoverBackground); }
      .export-icon { font-size: 1.1em; }
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
      .cat-header { 
        padding: 10px; 
        border-radius: 5px; 
        margin-bottom: 10px; 
        cursor: pointer; 
        display: flex; 
        justify-content: space-between; 
        align-items: center;
        user-select: none;
      }
      .cat-header:hover { opacity: 0.9; filter: brightness(1.1); }
      .cat-header.security { background: rgba(239, 68, 68, 0.2); }
      .cat-header.bug { background: rgba(245, 158, 11, 0.2); }
      .cat-header.performance { background: rgba(59, 130, 246, 0.2); }
      .cat-header.maintainability { background: rgba(16, 185, 129, 0.2); }
      .cat-title { display: flex; align-items: center; gap: 8px; }
      .cat-count { font-size: 0.8em; opacity: 0.7; }
      .chevron { transition: transform 0.3s; }
      .cat-header.collapsed .chevron { transform: rotate(-90deg); }
      .issues-list { display: flex; flex-direction: column; gap: 15px; transition: all 0.3s ease; }
      .issues-list.hidden { display: none; }
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
      // Get VS Code API
      const vscode = acquireVsCodeApi();
      
      // Export function
      function exportReport() {
        vscode.postMessage({ command: 'export' });
      }
      
      // Load selected scan
      function loadSelectedScan(scanId) {
        if (scanId) {
          vscode.postMessage({ command: 'loadScan', scanId: scanId });
        }
      }
      
      // Toggle category visibility
      function toggleCategory(header) {
        const issuesList = header.nextElementSibling;
        issuesList.classList.toggle('hidden');
        header.classList.toggle('collapsed');
      }
      
      // Tab switching logic
      // Tab switching logic
      document.addEventListener('DOMContentLoaded', () => {
        document.querySelectorAll('.tab-btn').forEach(btn => {
          btn.addEventListener('click', () => {
            // Remove active class from all tabs and contents
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            
            // Add active class to clicked tab
            btn.classList.add('active');
            
            // Show corresponding content
            const tabId = btn.dataset.tab;
            const content = document.getElementById(tabId + '-content');
            if (content) {
              content.classList.add('active');
            }
          });
        });
      });
    `;
    }
    async handleExport() {
        if (!this.currentScanId) {
            vscode.window.showErrorMessage('No scan ID available for export.');
            return;
        }
        if (!this.serverClient) {
            vscode.window.showErrorMessage('Server client not available.');
            return;
        }
        try {
            const format = await vscode.window.showQuickPick(['markdown', 'html', 'pdf', 'csv', 'excel', 'text', 'word'], { placeHolder: 'Select export format' });
            if (!format) {
                return;
            }
            const content = await this.serverClient.exportReport(this.currentScanId, format);
            // Determine file extension
            let extension = format;
            if (format === 'excel')
                extension = 'xlsx';
            if (format === 'word')
                extension = 'docx';
            if (format === 'text')
                extension = 'txt';
            // Save to file
            const uri = await vscode.window.showSaveDialog({
                defaultUri: vscode.Uri.file(`codereviewpro-report.${extension}`),
                filters: {
                    [format.toUpperCase()]: [extension],
                },
            });
            if (uri) {
                await vscode.workspace.fs.writeFile(uri, content);
                vscode.window.showInformationMessage(`Report exported to ${uri.fsPath}`);
            }
        }
        catch (error) {
            vscode.window.showErrorMessage(`Export failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
        }
    }
    async handleLoadScan(scanId) {
        if (!this.serverClient) {
            vscode.window.showErrorMessage('Server client not available.');
            return;
        }
        try {
            // Get the scan results
            const scanResult = await this.serverClient.getScanResults(scanId);
            // Get comparison (will be with previous scan if available)
            const comparison = await this.serverClient.compareScans(scanId);
            // Update the current scan ID
            this.currentScanId = scanId;
            // Update the webview with the new scan
            if (this.panel) {
                this.panel.webview.html = this.getHtmlContent(comparison);
            }
        }
        catch (error) {
            vscode.window.showErrorMessage(`Failed to load scan: ${error instanceof Error ? error.message : 'Unknown error'}`);
        }
    }
    dispose() {
        if (this.panel) {
            this.panel.dispose();
        }
    }
}
exports.ReportView = ReportView;
//# sourceMappingURL=reportView.js.map