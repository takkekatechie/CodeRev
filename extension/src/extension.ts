/**
 * Main extension entry point for CodeReviewPro
 */

import * as vscode from 'vscode';
import { ServerClient } from './serverClient';
import { DiagnosticProvider } from './diagnosticProvider';
import { ReportView } from './reportView';
import { ScanRequest } from './types';

let serverClient: ServerClient;
let diagnosticProvider: DiagnosticProvider;
let reportView: ReportView;
let statusBarItem: vscode.StatusBarItem;

export function activate(context: vscode.ExtensionContext) {
    console.log('CodeReviewPro extension is now active');

    // Initialize components
    serverClient = new ServerClient();
    diagnosticProvider = new DiagnosticProvider();
    reportView = new ReportView(context.extensionUri, serverClient);

    // Create status bar item
    statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 100);
    statusBarItem.text = '$(search) CodeReviewPro';
    statusBarItem.command = 'codereviewpro.scanWorkspace';
    statusBarItem.show();
    context.subscriptions.push(statusBarItem);

    // Register commands
    context.subscriptions.push(
        vscode.commands.registerCommand('codereviewpro.scanWorkspace', scanWorkspace),
        vscode.commands.registerCommand('codereviewpro.viewReport', viewReport),
        vscode.commands.registerCommand('codereviewpro.compareScans', compareScans),
        vscode.commands.registerCommand('codereviewpro.exportReport', exportReport),
        vscode.commands.registerCommand('codereviewpro.configureSettings', configureSettings)
    );

    // Register providers
    context.subscriptions.push(diagnosticProvider);

    // Check server health on activation
    checkServerHealth();
}

async function checkServerHealth() {
    const isHealthy = await serverClient.checkHealth();
    if (!isHealthy) {
        const action = await vscode.window.showWarningMessage(
            'CodeReviewPro backend server is not running. Please start the server to use the extension.',
            'Open Documentation'
        );
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
    const excludePatterns = config.get<string[]>('excludePatterns', []);
    const confirmLargeScan = config.get<boolean>('confirmLargeScan', true);

    // Prepare scan request
    const scanRequest: ScanRequest = {
        repositoryPath: workspaceRoot,
        excludePatterns,
    };

    try {
        // Show progress
        await vscode.window.withProgress(
            {
                location: vscode.ProgressLocation.Notification,
                title: 'CodeReviewPro',
                cancellable: false,
            },
            async (progress) => {
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
                    } else if (status.status === 'failed') {
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
                await reportView.show(comparison);

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
            }
        );
    } catch (error) {
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
        await reportView.show(comparison);
    } catch (error) {
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

        const previousScan = await vscode.window.showQuickPick(
            items.filter(item => item.scanId !== currentScan.scanId),
            { placeHolder: 'Select previous scan to compare with' }
        );

        if (!previousScan) {
            return;
        }

        const comparison = await serverClient.compareScans(currentScan.scanId, previousScan.scanId);
        await reportView.show(comparison);
    } catch (error) {
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

        const format = await vscode.window.showQuickPick(
            ['markdown', 'html', 'pdf', 'csv', 'excel', 'text', 'word'],
            { placeHolder: 'Select export format' }
        );

        if (!format) {
            return;
        }

        const content = await serverClient.exportReport(latestScan.scanId, format as any);

        // Determine file extension
        let extension = format;
        if (format === 'excel') extension = 'xlsx';
        if (format === 'word') extension = 'docx';
        if (format === 'text') extension = 'txt';

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
    } catch (error) {
        vscode.window.showErrorMessage(`Failed to export report: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
}

async function configureSettings() {
    vscode.commands.executeCommand('workbench.action.openSettings', 'codereviewpro');
}

export function deactivate() {
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
