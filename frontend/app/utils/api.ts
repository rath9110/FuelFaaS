// API client for FuelGuard AI backend

import type {
    FuelTransaction,
    Vehicle,
    Project,
    Worker,
    AnomalyResult,
    StatsResponse,
    LoginRequest,
    TokenResponse,
} from '../types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';
const API_VERSION = '/api/v1';

class ApiClient {
    private baseUrl: string;
    private token: string | null = null;

    constructor() {
        this.baseUrl = `${API_BASE_URL}${API_VERSION}`;

        // Load token from localStorage if available
        if (typeof window !== 'undefined') {
            this.token = localStorage.getItem('access_token');
        }
    }

    private getHeaders(): HeadersInit {
        const headers: HeadersInit = {
            'Content-Type': 'application/json',
        };

        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        return headers;
    }

    private async request<T>(
        endpoint: string,
        options: RequestInit = {}
    ): Promise<T> {
        const url = `${this.baseUrl}${endpoint}`;
        const config: RequestInit = {
            ...options,
            headers: {
                ...this.getHeaders(),
                ...options.headers,
            },
        };

        const response = await fetch(url, config);

        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: 'An error occurred' }));
            throw new Error(error.detail || `HTTP error! status: ${response.status}`);
        }

        if (response.status === 204) {
            return {} as T;
        }

        return response.json();
    }

    // Auth
    async login(credentials: LoginRequest): Promise<TokenResponse> {
        const response = await this.request<TokenResponse>('/auth/login', {
            method: 'POST',
            body: JSON.stringify(credentials),
        });

        this.token = response.access_token;
        if (typeof window !== 'undefined') {
            localStorage.setItem('access_token', response.access_token);
            localStorage.setItem('refresh_token', response.refresh_token);
        }

        return response;
    }

    logout(): void {
        this.token = null;
        if (typeof window !== 'undefined') {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
        }
    }

    // Transactions
    async getTransactions(params?: Record<string, any>): Promise<FuelTransaction[]> {
        const queryParams = new URLSearchParams();
        if (params) {
            Object.entries(params).forEach(([key, value]) => {
                if (value !== undefined) queryParams.append(key, String(value));
            });
        }
        return this.request<FuelTransaction[]>(`/transactions/?${queryParams.toString()}`);
    }

    // Vehicles
    async getVehicles(params?: Record<string, any>): Promise<Vehicle[]> {
        const queryParams = new URLSearchParams();
        if (params) {
            Object.entries(params).forEach(([key, value]) => {
                if (value !== undefined) queryParams.append(key, String(value));
            });
        }
        return this.request<Vehicle[]>(`/vehicles/?${queryParams.toString()}`);
    }

    async createVehicle(vehicle: Partial<Vehicle>): Promise<Vehicle> {
        return this.request<Vehicle>('/vehicles/', { method: 'POST', body: JSON.stringify(vehicle) });
    }

    async updateVehicle(id: string, updates: Partial<Vehicle>): Promise<Vehicle> {
        return this.request<Vehicle>(`/vehicles/${id}`, { method: 'PATCH', body: JSON.stringify(updates) });
    }

    async deleteVehicle(id: string): Promise<void> {
        return this.request<void>(`/vehicles/${id}`, { method: 'DELETE' });
    }

    // Projects
    async getProjects(params?: Record<string, any>): Promise<Project[]> {
        const queryParams = new URLSearchParams();
        if (params) {
            Object.entries(params).forEach(([key, value]) => {
                if (value !== undefined) queryParams.append(key, String(value));
            });
        }
        return this.request<Project[]>(`/projects/?${queryParams.toString()}`);
    }

    async createProject(project: Partial<Project>): Promise<Project> {
        return this.request<Project>('/projects/', { method: 'POST', body: JSON.stringify(project) });
    }

    async updateProject(id: string, updates: Partial<Project>): Promise<Project> {
        return this.request<Project>(`/projects/${id}`, { method: 'PATCH', body: JSON.stringify(updates) });
    }

    async deleteProject(id: string): Promise<void> {
        return this.request<void>(`/projects/${id}`, { method: 'DELETE' });
    }

    // Workers
    async getWorkers(params?: Record<string, any>): Promise<Worker[]> {
        const queryParams = new URLSearchParams();
        if (params) {
            Object.entries(params).forEach(([key, value]) => {
                if (value !== undefined) queryParams.append(key, String(value));
            });
        }
        return this.request<Worker[]>(`/workers/?${queryParams.toString()}`);
    }

    async createWorker(worker: Partial<Worker>): Promise<Worker> {
        return this.request<Worker>('/workers/', { method: 'POST', body: JSON.stringify(worker) });
    }

    async updateWorker(id: string, updates: Partial<Worker>): Promise<Worker> {
        return this.request<Worker>(`/workers/${id}`, { method: 'PATCH', body: JSON.stringify(updates) });
    }

    async deleteWorker(id: string): Promise<void> {
        return this.request<void>(`/workers/${id}`, { method: 'DELETE' });
    }

    // Anomalies
    async getAnomalies(params?: Record<string, any>): Promise<AnomalyResult[]> {
        const queryParams = new URLSearchParams();
        if (params) {
            Object.entries(params).forEach(([key, value]) => {
                if (value !== undefined) queryParams.append(key, String(value));
            });
        }
        return this.request<AnomalyResult[]>(`/anomalies/?${queryParams.toString()}`);
    }

    async reviewAnomaly(id: number, review: any): Promise<AnomalyResult> {
        return this.request<AnomalyResult>(`/anomalies/${id}`, { method: 'PATCH', body: JSON.stringify(review) });
    }

    // Stats
    async getStats(): Promise<StatsResponse> {
        return this.request<StatsResponse>('/stats/');
    }
}

export const api = new ApiClient();
export default api;
