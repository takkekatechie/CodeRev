/**
 * Type definitions for CodeReviewPro
 */

export interface ScanRequest {
    repositoryPath: string;
    recentOnly?: boolean;
    days?: number;
    excludePatterns?: string[];
}

export interface ScanResponse {
    scanId: string;
    status: 'started' | 'running' | 'completed' | 'failed';
    message?: string;
    progress?: number;
}

export interface Issue {
    id: string;
    category: IssueCategory;
    severity: IssueSeverity;
    filePath: string;
    lineStart: number;
    lineEnd: number;
    description: string;
    recommendation: string;
    codeSnippet?: string;
    issueHash: string;
}

export type IssueCategory =
    | 'bug'
    | 'security'
    | 'performance'
    | 'maintainability'
    | 'architecture';

export type IssueSeverity = 'error' | 'warning' | 'info';

export type IssueStatus = 'new' | 'fixed' | 'remaining';

export interface ScanResult {
    scanId: string;
    scanDate: string;
    repositoryPath: string;
    detectedLanguages: string[];
    detectedFrameworks: string[];
    totalFiles: number;
    issues: Issue[];
    summary: ScanSummary;
}

export interface ScanSummary {
    totalIssues: number;
    newIssues: number;
    fixedIssues: number;
    remainingIssues: number;
    issuesByCategory: Record<IssueCategory, number>;
    issuesBySeverity: Record<IssueSeverity, number>;
}

export interface ComparisonResult {
    currentScan: ScanResult;
    previousScan?: ScanResult;
    newIssues: Issue[];
    fixedIssues: Issue[];
    remainingIssues: Issue[];
}

export interface EnvironmentInfo {
    primaryLanguage: string;
    frameworks: string[];
    buildTools: string[];
}

export interface ProgressUpdate {
    scanId: string;
    progress: number;
    currentFile?: string;
    message: string;
}
