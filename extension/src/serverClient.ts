/**
 * Client for communicating with the CodeReviewPro backend server
 */

import axios, { AxiosInstance } from 'axios';
import * as vscode from 'vscode';
import { ScanRequest, ScanResponse, ScanResult, ComparisonResult } from './types';

export class ServerClient {
    private client: AxiosInstance;
    private serverUrl: string;

    constructor() {
        this.serverUrl = this.getServerUrl();
        this.client = axios.create({
            baseURL: this.serverUrl,
            timeout: 300000, // 5 minutes for long-running scans
            headers: {
                'Content-Type': 'application/json',
            },
        });
    }

    private getServerUrl(): string {
        const config = vscode.workspace.getConfiguration('codereviewpro');
        return config.get<string>('serverUrl', 'http://localhost:5000');
    }

    /**
     * Check if the backend server is running
     */
    async checkHealth(): Promise<boolean> {
        try {
            const response = await this.client.get('/health');
            return response.status === 200;
        } catch (error) {
            return false;
        }
    }

    /**
     * Start a new scan
     */
    async startScan(request: ScanRequest): Promise<ScanResponse> {
        try {
            const response = await this.client.post<ScanResponse>('/api/scan', request);
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(`Failed to start scan: ${error.message}`);
            }
            throw error;
        }
    }

    /**
     * Get scan status
     */
    async getScanStatus(scanId: string): Promise<ScanResponse> {
        try {
            const response = await this.client.get<ScanResponse>(`/api/scan/${scanId}/status`);
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(`Failed to get scan status: ${error.message}`);
            }
            throw error;
        }
    }

    /**
     * Get scan results
     */
    async getScanResults(scanId: string): Promise<ScanResult> {
        try {
            const response = await this.client.get<ScanResult>(`/api/scan/${scanId}/results`);
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(`Failed to get scan results: ${error.message}`);
            }
            throw error;
        }
    }

    /**
     * Get latest scan for a repository
     */
    async getLatestScan(repositoryPath: string): Promise<ScanResult | null> {
        try {
            const response = await this.client.get<ScanResult>('/api/scan/latest', {
                params: { repository_path: repositoryPath },
            });
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error) && error.response?.status === 404) {
                return null;
            }
            throw error;
        }
    }

    /**
     * Compare two scans
     */
    async compareScans(currentScanId: string, previousScanId?: string): Promise<ComparisonResult> {
        try {
            const response = await this.client.post<ComparisonResult>('/api/scan/compare', {
                current_scan_id: currentScanId,
                previous_scan_id: previousScanId,
            });
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(`Failed to compare scans: ${error.message}`);
            }
            throw error;
        }
    }

    /**
     * Get scan history for a repository
     */
    async getScanHistory(repositoryPath: string): Promise<ScanResult[]> {
        try {
            const response = await this.client.get<ScanResult[]>('/api/scan/history', {
                params: { repository_path: repositoryPath },
            });
            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(`Failed to get scan history: ${error.message}`);
            }
            throw error;
        }
    }

    /**
     * Export report in specified format
     */
    async exportReport(scanId: string, format: 'markdown' | 'html' | 'pdf' | 'csv' | 'excel' | 'text' | 'word'): Promise<Buffer> {
        try {
            const response = await this.client.get<{ content: string, is_binary: boolean }>(`/api/scan/${scanId}/export`, {
                params: { format },
            });

            if (response.data.is_binary) {
                return Buffer.from(response.data.content, 'base64');
            } else {
                return Buffer.from(response.data.content, 'utf-8');
            }
        } catch (error) {
            if (axios.isAxiosError(error)) {
                throw new Error(`Failed to export report: ${error.message}`);
            }
            throw error;
        }
    }
}
