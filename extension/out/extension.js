"use strict";
/**
 * Main extension entry point for CodeReviewPro
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
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = __importStar(require("vscode"));
const serverClient_1 = require("./serverClient");
const diagnosticProvider_1 = require("./diagnosticProvider");
const reportView_1 = require("./reportView");
let serverClient;
let diagnosticProvider;
let reportView;
let statusBarItem;
function activate(context) {
    console.log('CodeReviewPro extension is now active');
    // Initialize components
    serverClient = new serverClient_1.ServerClient();
    diagnosticProvider = new diagnosticProvider_1.DiagnosticProvider();
    reportView = new reportView_1.ReportView(context.extensionUri);
    // Create status bar item
    statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 100);
    statusBarItem.text = '$(search) CodeReviewPro';
    statusBarItem.command = 'codereviewpro.scanWorkspace';
    statusBarItem.show();
    context.subscriptions.push(statusBarItem);
    // Register commands
    context.subscriptions.push(vscode.commands.registerCommand('codereviewpro.scanWorkspace', scanWorkspace), vscode.commands.registerCommand('codereviewpro.viewReport', viewReport), vscode.commands.registerCommand('codereviewpro.compareScans', compareScans), vscode.commands.registerCommand('codereviewpro.exportReport', exportReport), vscode.commands.registerCommand('codereviewpro.configureSettings', configureSettings));
    // Register providers
    context.subscriptions.push(diagnosticProvider);
    // Check server health on activation
    checkServerHealth();
}
async function checkServerHealth() {
    const isHealthy = await serverClient.checkHealth();
    if (!isHealthy) {
        const action = await vscode.window.showWarningMessage('CodeReviewPro backend server is not running. Please start the server to use the extension.', 'Open Documentation');
        if (action === 'Open Documentation') {
            vscode.env.openExternal(vscode.Uri.parse('https://github.com/codereviewpro/docs'));
        }
    }
}
async function scanWorkspace() {
    const workspaceFolders = vscode.workspace.workspaceFolders;
    if (!workspaceFolders || workspaceFolders.length === 0) {
        vscode.window.showErrorMessage('No workspace folder is open. Please open a folder to scan.');
        return;
    }
    const workspaceRoot = workspaceFolders[0].uri.fsPath;
    // Check server health
    const isHealthy = await serverClient.checkHealth();
    if (!isHealthy) {
        vscode.window.showErrorMessage('Backend server is not running. Please start the server first.');
        return;
    }
    // Get configuration
    const config = vscode.workspace.getConfiguration('codereviewpro');
    const excludePatterns = config.get('excludePatterns', []);
    const confirmLargeScan = config.get('confirmLargeScan', true);
    // Prepare scan request
    const scanRequest = {
        repositoryPath: workspaceRoot,
        excludePatterns,
    };
    try {
        // Show progress
        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'CodeReviewPro',
            cancellable: false,
        }, async (progress) => {
            progress.report({ message: 'Starting scan...' });
            statusBarItem.text = '$(sync~spin) Scanning...';
            // Start scan
            const scanResponse = await serverClient.startScan(scanRequest);
            const scanId = scanResponse.scanId;
            progress.report({ message: 'Analyzing code...' });
            // Poll for completion
            let isComplete = false;
            while (!isComplete) {
                await new Promise(resolve => setTimeout(resolve, 2000)); // Poll every 2 seconds
                const status = await serverClient.getScanStatus(scanId);
                if (status.status === 'completed') {
                    isComplete = true;
                }
                else if (status.status === 'failed') {
                    throw new Error(status.message || 'Scan failed');
                }
                if (status.progress !== undefined) {
                    progress.report({
                        message: `Analyzing... ${Math.round(status.progress)}%`,
                        increment: status.progress
                    });
                }
            }
            progress.report({ message: 'Generating report...' });
            // Get results
            const scanResult = await serverClient.getScanResults(scanId);
            // Get comparison with previous scan
            const comparison = await serverClient.compareScans(scanId);
            // Update diagnostics
            diagnosticProvider.updateDiagnostics(scanResult, workspaceRoot);
            // Show report
            reportView.show(comparison);
            statusBarItem.text = '$(check) Scan Complete';
            setTimeout(() => {
                statusBarItem.text = '$(search) CodeReviewPro';
            }, 3000);
            // Show summary
            const totalIssues = scanResult.summary.totalIssues;
            const newIssues = comparison.newIssues.length;
            const fixedIssues = comparison.fixedIssues.length;
            let message = `Scan complete! Found ${totalIssues} total issue(s)`;
            if (newIssues > 0) {
                message += `, ${newIssues} new`;
            }
            if (fixedIssues > 0) {
                message += `, ${fixedIssues} fixed`;
            }
            vscode.window.showInformationMessage(message);
        });
    }
    catch (error) {
        statusBarItem.text = '$(error) Scan Failed';
        setTimeout(() => {
            statusBarItem.text = '$(search) CodeReviewPro';
        }, 3000);
        vscode.window.showErrorMessage(`Scan failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
}
async function viewReport() {
    const workspaceFolders = vscode.workspace.workspaceFolders;
    if (!workspaceFolders || workspaceFolders.length === 0) {
        vscode.window.showErrorMessage('No workspace folder is open.');
        return;
    }
    const workspaceRoot = workspaceFolders[0].uri.fsPath;
    try {
        const latestScan = await serverClient.getLatestScan(workspaceRoot);
        if (!latestScan) {
            vscode.window.showInformationMessage('No scan results found. Please run a scan first.');
            return;
        }
        const comparison = await serverClient.compareScans(latestScan.scanId);
        reportView.show(comparison);
    }
    catch (error) {
        vscode.window.showErrorMessage(`Failed to view report: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
}
async function compareScans() {
    const workspaceFolders = vscode.workspace.workspaceFolders;
    if (!workspaceFolders || workspaceFolders.length === 0) {
        vscode.window.showErrorMessage('No workspace folder is open.');
        return;
    }
    const workspaceRoot = workspaceFolders[0].uri.fsPath;
    try {
        const history = await serverClient.getScanHistory(workspaceRoot);
        if (history.length < 2) {
            vscode.window.showInformationMessage('Need at least 2 scans to compare. Please run more scans.');
            return;
        }
        // Show quick pick for scan selection
        const items = history.map(scan => ({
            label: new Date(scan.scanDate).toLocaleString(),
            description: `${scan.summary.totalIssues} issues`,
            scanId: scan.scanId,
        }));
        const currentScan = await vscode.window.showQuickPick(items, {
            placeHolder: 'Select current scan',
        });
        if (!currentScan) {
            return;
        }
        const previousScan = await vscode.window.showQuickPick(items.filter(item => item.scanId !== currentScan.scanId), { placeHolder: 'Select previous scan to compare with' });
        if (!previousScan) {
            return;
        }
        const comparison = await serverClient.compareScans(currentScan.scanId, previousScan.scanId);
        reportView.show(comparison);
    }
    catch (error) {
        vscode.window.showErrorMessage(`Failed to compare scans: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
}
async function exportReport() {
    const workspaceFolders = vscode.workspace.workspaceFolders;
    if (!workspaceFolders || workspaceFolders.length === 0) {
        vscode.window.showErrorMessage('No workspace folder is open.');
        return;
    }
    const workspaceRoot = workspaceFolders[0].uri.fsPath;
    try {
        const latestScan = await serverClient.getLatestScan(workspaceRoot);
        if (!latestScan) {
            vscode.window.showInformationMessage('No scan results found. Please run a scan first.');
            return;
        }
        const format = await vscode.window.showQuickPick(['markdown', 'html', 'pdf', 'csv', 'excel', 'text', 'word'], { placeHolder: 'Select export format' });
        if (!format) {
            return;
        }
        const content = await serverClient.exportReport(latestScan.scanId, format);
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
        vscode.window.showErrorMessage(`Failed to export report: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
}
async function configureSettings() {
    vscode.commands.executeCommand('workbench.action.openSettings', 'codereviewpro');
}
function deactivate() {
    if (diagnosticProvider) {
        diagnosticProvider.dispose();
    }
    if (reportView) {
        reportView.dispose();
    }
    if (statusBarItem) {
        statusBarItem.dispose();
    }
}
//# sourceMappingURL=extension.js.map