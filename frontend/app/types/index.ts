// TypeScript interfaces matching backend models

export interface FuelTransaction {
    id?: number;
    transaction_id: string;
    provider: 'okq8' | 'preem' | 'shell' | 'circlek';
    card_id: string;
    vehicle_id: string;
    driver_id?: string;
    timestamp: string;
    liters: number;
    price_per_liter: number;
    total_amount: number;
    fuel_type: string;
    station_id: string;
    station_lat: number;
    station_lon: number;
    company_id?: string;
    created_at?: string;
}

export interface Vehicle {
    id?: number;
    vehicle_id: string;
    type: string;
    tank_capacity_liters: number;
    reg_number: string;
    assigned_to_project?: string;
    status: 'active' | 'inactive';
    company_id?: string;
    created_at?: string;
    updated_at?: string;
}

export interface Project {
    id?: number;
    project_id: string;
    name: string;
    geofence_lat: number;
    geofence_lon: number;
    geofence_radius_km: number;
    active: boolean;
    company_id?: string;
    start_date?: string;
    end_date?: string;
    created_at?: string;
    updated_at?: string;
}

export interface Worker {
    id?: number;
    worker_id: string;
    name: string;
    schedule_start: string;
    schedule_end: string;
    assigned_project_ids: string[];
    company_id?: string;
    is_active: boolean;
    created_at?: string;
    updated_at?: string;
}

export interface AnomalyResult {
    id?: number;
    transaction_id: string;
    is_anomalous: boolean;
    severity: 'Low' | 'Medium' | 'High' | 'Critical';
    risk_score: number;
    reasons: string[];
    reviewed: boolean;
    reviewed_by?: number;
    reviewed_at?: string;
    review_notes?: string;
    status: 'pending' | 'confirmed' | 'false_positive' | 'resolved';
    detected_at?: string;
}

export interface User {
    id: number;
    email: string;
    username: string;
    full_name?: string;
    role: 'admin' | 'manager' | 'viewer';
    is_active: boolean;
    last_login?: string;
    created_at?: string;
    updated_at?: string;
}

export interface StatsResponse {
    total_transactions: number;
    total_anomalies: number;
    average_risk_score: number;
    critical_anomalies: number;
    high_anomalies: number;
    medium_anomalies: number;
    low_anomalies: number;
}

export interface LoginRequest {
    username: string;
    password: string;
}

export interface TokenResponse {
    access_token: string;
    refresh_token: string;
    token_type: string;
    user: User;
}
