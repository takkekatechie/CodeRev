"use strict";
/**
 * Diagnostic provider for VS Code integration
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
exports.DiagnosticProvider = void 0;
const vscode = __importStar(require("vscode"));
class DiagnosticProvider {
    constructor() {
        this.diagnosticCollection = vscode.languages.createDiagnosticCollection('codereviewpro');
        this.severityMapping = this.loadSeverityMapping();
    }
    loadSeverityMapping() {
        const config = vscode.workspace.getConfiguration('codereviewpro');
        const severityLevels = config.get('severityLevels', {
            security: 'error',
            bug: 'error',
            performance: 'warning',
            maintainability: 'info',
            architecture: 'info',
        });
        const mapping = new Map();
        for (const [category, severity] of Object.entries(severityLevels)) {
            mapping.set(category, this.mapSeverity(severity));
        }
        return mapping;
    }
    mapSeverity(severity) {
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
    updateDiagnostics(scanResult, workspaceRoot) {
        // Clear existing diagnostics
        this.diagnosticCollection.clear();
        // Group issues by file
        const issuesByFile = new Map();
        for (const issue of scanResult.issues) {
            const filePath = issue.filePath;
            if (!issuesByFile.has(filePath)) {
                issuesByFile.set(filePath, []);
            }
            issuesByFile.get(filePath).push(issue);
        }
        // Create diagnostics for each file
        for (const [filePath, issues] of issuesByFile) {
            const uri = vscode.Uri.file(filePath);
            const diagnostics = [];
            for (const issue of issues) {
                const diagnostic = this.createDiagnostic(issue);
                diagnostics.push(diagnostic);
            }
            this.diagnosticCollection.set(uri, diagnostics);
        }
    }
    createDiagnostic(issue) {
        // Create range (VS Code uses 0-based line numbers)
        const range = new vscode.Range(Math.max(0, issue.lineStart - 1), 0, Math.max(0, issue.lineEnd - 1), Number.MAX_SAFE_INTEGER);
        // Determine severity
        const severity = this.severityMapping.get(issue.category) || vscode.DiagnosticSeverity.Warning;
        // Create diagnostic
        const diagnostic = new vscode.Diagnostic(range, issue.description, severity);
        diagnostic.source = 'CodeReviewPro';
        diagnostic.code = issue.category;
        // Add related information with recommendation
        if (issue.recommendation) {
            diagnostic.relatedInformation = [
                new vscode.DiagnosticRelatedInformation(new vscode.Location(vscode.Uri.file(issue.filePath), range), `💡 Recommendation: ${issue.recommendation}`),
            ];
        }
        return diagnostic;
    }
    /**
     * Clear all diagnostics
     */
    clear() {
        this.diagnosticCollection.clear();
    }
    /**
     * Dispose of the diagnostic collection
     */
    dispose() {
        this.diagnosticCollection.dispose();
    }
}
exports.DiagnosticProvider = DiagnosticProvider;
//# sourceMappingURL=diagnosticProvider.js.map