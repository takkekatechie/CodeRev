/**
 * Diagnostic provider for VS Code integration
 */

import * as vscode from 'vscode';
import { Issue, IssueSeverity, ScanResult } from './types';

export class DiagnosticProvider {
    private diagnosticCollection: vscode.DiagnosticCollection;
    private severityMapping: Map<string, vscode.DiagnosticSeverity>;

    constructor() {
        this.diagnosticCollection = vscode.languages.createDiagnosticCollection('codereviewpro');
        this.severityMapping = this.loadSeverityMapping();
    }

    private loadSeverityMapping(): Map<string, vscode.DiagnosticSeverity> {
        const config = vscode.workspace.getConfiguration('codereviewpro');
        const severityLevels = config.get<Record<string, string>>('severityLevels', {
            security: 'error',
            bug: 'error',
            performance: 'warning',
            maintainability: 'info',
            architecture: 'info',
        });

        const mapping = new Map<string, vscode.DiagnosticSeverity>();
        for (const [category, severity] of Object.entries(severityLevels)) {
            mapping.set(category, this.mapSeverity(severity as IssueSeverity));
        }
        return mapping;
    }

    private mapSeverity(severity: IssueSeverity): vscode.DiagnosticSeverity {
        switch (severity) {
            case 'error':
                return vscode.DiagnosticSeverity.Error;
            case 'warning':
                return vscode.DiagnosticSeverity.Warning;
            case 'info':
                return vscode.DiagnosticSeverity.Information;
            default:
                return vscode.DiagnosticSeverity.Warning;
        }
    }

    /**
     * Update diagnostics from scan results
     */
    updateDiagnostics(scanResult: ScanResult, workspaceRoot: string): void {
        // Clear existing diagnostics
        this.diagnosticCollection.clear();

        // Group issues by file
        const issuesByFile = new Map<string, Issue[]>();
        for (const issue of scanResult.issues) {
            const filePath = issue.filePath;
            if (!issuesByFile.has(filePath)) {
                issuesByFile.set(filePath, []);
            }
            issuesByFile.get(filePath)!.push(issue);
        }

        // Create diagnostics for each file
        for (const [filePath, issues] of issuesByFile) {
            const uri = vscode.Uri.file(filePath);
            const diagnostics: vscode.Diagnostic[] = [];

            for (const issue of issues) {
                const diagnostic = this.createDiagnostic(issue);
                diagnostics.push(diagnostic);
            }

            this.diagnosticCollection.set(uri, diagnostics);
        }
    }

    private createDiagnostic(issue: Issue): vscode.Diagnostic {
        // Create range (VS Code uses 0-based line numbers)
        const range = new vscode.Range(
            Math.max(0, issue.lineStart - 1),
            0,
            Math.max(0, issue.lineEnd - 1),
            Number.MAX_SAFE_INTEGER
        );

        // Determine severity
        const severity = this.severityMapping.get(issue.category) || vscode.DiagnosticSeverity.Warning;

        // Create diagnostic
        const diagnostic = new vscode.Diagnostic(
            range,
            issue.description,
            severity
        );

        diagnostic.source = 'CodeReviewPro';
        diagnostic.code = issue.category;

        // Add related information with recommendation
        if (issue.recommendation) {
            diagnostic.relatedInformation = [
                new vscode.DiagnosticRelatedInformation(
                    new vscode.Location(
                        vscode.Uri.file(issue.filePath),
                        range
                    ),
                    `💡 Recommendation: ${issue.recommendation}`
                ),
            ];
        }

        return diagnostic;
    }

    /**
     * Clear all diagnostics
     */
    clear(): void {
        this.diagnosticCollection.clear();
    }

    /**
     * Dispose of the diagnostic collection
     */
    dispose(): void {
        this.diagnosticCollection.dispose();
    }
}
