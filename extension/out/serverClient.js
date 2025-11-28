"use strict";
/**
 * Client for communicating with the CodeReviewPro backend server
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
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.ServerClient = void 0;
const axios_1 = __importDefault(require("axios"));
const vscode = __importStar(require("vscode"));
class ServerClient {
    constructor() {
        this.serverUrl = this.getServerUrl();
        this.client = axios_1.default.create({
            baseURL: this.serverUrl,
            timeout: 300000, // 5 minutes for long-running scans
            headers: {
                'Content-Type': 'application/json',
            },
        });
    }
    getServerUrl() {
        const config = vscode.workspace.getConfiguration('codereviewpro');
        return config.get('serverUrl', 'http://localhost:5000');
    }
    /**
     * Check if the backend server is running
     */
    async checkHealth() {
        try {
            const response = await this.client.get('/health');
            return response.status === 200;
        }
        catch (error) {
            return false;
        }
    }
    /**
     * Start a new scan
     */
    async startScan(request) {
        try {
            const response = await this.client.post('/api/scan', request);
            return response.data;
        }
        catch (error) {
            if (axios_1.default.isAxiosError(error)) {
                throw new Error(`Failed to start scan: ${error.message}`);
            }
            throw error;
        }
    }
    /**
     * Get scan status
     */
    async getScanStatus(scanId) {
        try {
            const response = await this.client.get(`/api/scan/${scanId}/status`);
            return response.data;
        }
        catch (error) {
            if (axios_1.default.isAxiosError(error)) {
                throw new Error(`Failed to get scan status: ${error.message}`);
            }
            throw error;
        }
    }
    /**
     * Get scan results
     */
    async getScanResults(scanId) {
        try {
            const response = await this.client.get(`/api/scan/${scanId}/results`);
            return response.data;
        }
        catch (error) {
            if (axios_1.default.isAxiosError(error)) {
                throw new Error(`Failed to get scan results: ${error.message}`);
            }
            throw error;
        }
    }
    /**
     * Get latest scan for a repository
     */
    async getLatestScan(repositoryPath) {
        try {
            const response = await this.client.get('/api/scan/latest', {
                params: { repository_path: repositoryPath },
            });
            return response.data;
        }
        catch (error) {
            if (axios_1.default.isAxiosError(error) && error.response?.status === 404) {
                return null;
            }
            throw error;
        }
    }
    /**
     * Compare two scans
     */
    async compareScans(currentScanId, previousScanId) {
        try {
            const response = await this.client.post('/api/scan/compare', {
                current_scan_id: currentScanId,
                previous_scan_id: previousScanId,
            });
            return response.data;
        }
        catch (error) {
            if (axios_1.default.isAxiosError(error)) {
                throw new Error(`Failed to compare scans: ${error.message}`);
            }
            throw error;
        }
    }
    /**
     * Get scan history for a repository
     */
    async getScanHistory(repositoryPath) {
        try {
            const response = await this.client.get('/api/scan/history', {
                params: { repository_path: repositoryPath },
            });
            return response.data;
        }
        catch (error) {
            if (axios_1.default.isAxiosError(error)) {
                throw new Error(`Failed to get scan history: ${error.message}`);
            }
            throw error;
        }
    }
    /**
     * Export report in specified format
     */
    async exportReport(scanId, format) {
        try {
            const response = await this.client.get(`/api/scan/${scanId}/export`, {
                params: { format },
            });
            if (response.data.is_binary) {
                return Buffer.from(response.data.content, 'base64');
            }
            else {
                return Buffer.from(response.data.content, 'utf-8');
            }
        }
        catch (error) {
            if (axios_1.default.isAxiosError(error)) {
                throw new Error(`Failed to export report: ${error.message}`);
            }
            throw error;
        }
    }
}
exports.ServerClient = ServerClient;
//# sourceMappingURL=serverClient.js.map