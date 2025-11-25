'use client';

import { useEffect, useState } from 'react';
import { StatsResponse, AnomalyResult } from '../types';
import { api } from '../utils/api';
import SeverityBadge from '../components/SeverityBadge';

export default function DashboardPage() {
    const [stats, setStats] = useState<StatsResponse | null>(null);
    const [anomalies, setAnomalies] = useState<AnomalyResult[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [statsData, anomaliesData] = await Promise.all([
                    api.getStats(),
                    api.getAnomalies({ limit: 5 })
                ]);
                setStats(statsData);
                setAnomalies(anomaliesData);
            } catch (error) {
                console.error('Error fetching dashboard data:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    if (loading) {
        return (
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
                <div className="spinner" />
            </div>
        );
    }

    return (
        <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
            <h1 style={{
                fontSize: '2rem',
                fontWeight: '700',
                marginBottom: 'var(--spacing-xl)',
                color: 'var(--text-primary)'
            }}>
                Dashboard
            </h1>

            {/* Stats Grid */}
            <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
                gap: 'var(--spacing-lg)',
                marginBottom: 'var(--spacing-2xl)'
            }}>
                <StatCard
                    title="Total Transactions"
                    value={stats?.total_transactions || 0}
                    icon="⛽"
                    color="var(--primary-600)"
                />
                <StatCard
                    title="Total Anomalies"
                    value={stats?.total_anomalies || 0}
                    icon="🚨"
                    color="var(--danger-600)"
                />
                <StatCard
                    title="Critical Alerts"
                    value={stats?.critical_anomalies || 0}
                    icon="⚠️"
                    color="var(--warning-600)"
                />
                <StatCard
                    title="Avg Risk Score"
                    value={Math.round(stats?.average_risk_score || 0)}
                    icon="📊"
                    color="var(--secondary-600)"
                />
            </div>

            {/* Recent Anomalies */}
            <div className="card">
                <h2 style={{
                    fontSize: '1.25rem',
                    fontWeight: '600',
                    marginBottom: 'var(--spacing-lg)',
                    color: 'var(--text-primary)'
                }}>
                    Recent Anomalies
                </h2>

                {anomalies.length === 0 ? (
                    <p style={{ color: 'var(--text-secondary)', textAlign: 'center', padding: 'var(--spacing-xl)' }}>
                        No anomalies detected. All systems normal! ✅
                    </p>
                ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-md)' }}>
                        {anomalies.map((anomaly) => (
                            <div
                                key={anomaly.id}
                                className="card"
                                style={{
                                    padding: 'var(--spacing-md)',
                                    display: 'flex',
                                    justifyContent: 'space-between',
                                    alignItems: 'center',
                                    cursor: 'pointer'
                                }}
                            >
                                <div style={{ flex: 1 }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-md)', marginBottom: 'var(--spacing-xs)' }}>
                                        <SeverityBadge severity={anomaly.severity} />
                                        <span style={{ fontWeight: '500', color: 'var(--text-primary)' }}>
                                            {anomaly.transaction_id}
                                        </span>
                                    </div>
                                    <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                                        {anomaly.reasons[0]}
                                        {anomaly.reasons.length > 1 && ` +${anomaly.reasons.length - 1} more`}
                                    </p>
                                </div>
                                <div style={{
                                    fontSize: '1.5rem',
                                    fontWeight: '700',
                                    color: 'var(--primary-600)'
                                }}>
                                    {anomaly.risk_score}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}

function StatCard({ title, value, icon, color }: { title: string; value: number; icon: string; color: string }) {
    return (
        <div
            className="card animate-slide-up"
            style={{
                position: 'relative',
                overflow: 'hidden'
            }}
        >
            <div style={{
                position: 'absolute',
                top: '10px',
                right: '10px',
                fontSize: '3rem',
                opacity: '0.1'
            }}>
                {icon}
            </div>
            <p style={{
                fontSize: '0.875rem',
                fontWeight: '500',
                color: 'var(--text-secondary)',
                marginBottom: 'var(--spacing-sm)'
            }}>
                {title}
            </p>
            <p style={{
                fontSize: '2.5rem',
                fontWeight: '700',
                color
            }}>
                {value.toLocaleString()}
            </p>
        </div>
    );
}
