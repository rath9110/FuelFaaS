'use client';

import { useEffect, useState } from 'react';
import { AnomalyResult } from '../../types';
import { api } from '../../utils/api';
import SeverityBadge from '../../components/SeverityBadge';

export default function AnomaliesPage() {
    const [anomalies, setAnomalies] = useState<AnomalyResult[]>([]);
    const [loading, setLoading] = useState(true);
    const [severityFilter, setSeverityFilter] = useState<string>('');

    useEffect(() => {
        fetchAnomalies();
    }, [severityFilter]);

    const fetchAnomalies = async () => {
        try {
            const params = severityFilter ? { severity: severityFilter } : {};
            const data = await api.getAnomalies({ ...params, limit: 50 });
            setAnomalies(data);
        } catch (error) {
            console.error('Error fetching anomalies:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--spacing-xl)' }}>
                <h1 style={{ fontSize: '2rem', fontWeight: '700', color: 'var(--text-primary)' }}>
                    Fraud Anomalies
                </h1>
                <select
                    value={severityFilter}
                    onChange={(e) => setSeverityFilter(e.target.value)}
                    style={{
                        padding: 'var(--spacing-sm) var(--spacing-md)',
                        borderRadius: 'var(--radius-md)',
                        border: '1px solid var(--border-color)',
                        fontSize: '0.875rem'
                    }}
                >
                    <option value="">All Severities</option>
                    <option value="Critical">Critical</option>
                    <option value="High">High</option>
                    <option value="Medium">Medium</option>
                    <option value="Low">Low</option>
                </select>
            </div>

            {loading ? (
                <div style={{ display: 'flex', justifyContent: 'center', padding: 'var(--spacing-2xl)' }}>
                    <div className="spinner" />
                </div>
            ) : (
                <div style={{ display: 'grid', gap: 'var(--spacing-lg)' }}>
                    {anomalies.map((anomaly) => (
                        <div key={anomaly.id} className="card animate-slide-up" style={{
                            display: 'flex',
                            gap: 'var(--spacing-lg)'
                        }}>
                            {/* Left Side - Score */}
                            <div style={{
                                display: 'flex',
                                flexDirection: 'column',
                                alignItems: 'center',
                                justifyContent: 'center',
                                minWidth: '80px',
                                borderRight: '1px solid var(--border-color)',
                                paddingRight: 'var(--spacing-lg)'
                            }}>
                                <div style={{
                                    fontSize: '2.5rem',
                                    fontWeight: '700',
                                    color: anomaly.risk_score > 70 ? 'var(--danger-600)' : anomaly.risk_score > 40 ? 'var(--warning-600)' : 'var(--secondary-600)'
                                }}>
                                    {anomaly.risk_score}
                                </div>
                                <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>
                                    Risk
                                </div>
                            </div>

                            {/* Right Side - Details */}
                            <div style={{ flex: 1 }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: 'var(--spacing-md)' }}>
                                    <div>
                                        <div style={{ display: 'flex', gap: 'var(--spacing-md)', alignItems: 'center', marginBottom: 'var(--spacing-sm)' }}>
                                            <SeverityBadge severity={anomaly.severity} />
                                            <span style={{ fontFamily: 'monospace', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                                                {anomaly.transaction_id}
                                            </span>
                                        </div>
                                        <div style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)' }}>
                                            {anomaly.detected_at && new Date(anomaly.detected_at).toLocaleString()}
                                        </div>
                                    </div>
                                    <span className={`badge ${anomaly.reviewed ? 'badge-low' : 'badge-medium'}`}>
                                        {anomaly.status}
                                    </span>
                                </div>

                                <div style={{ marginBottom: 'var(--spacing-md)' }}>
                                    <h4 style={{ fontSize: '0.875rem', fontWeight: '600', color: 'var(--text-secondary)', marginBottom: 'var(--spacing-xs)' }}>
                                        Fraud Indicators ({anomaly.reasons.length})
                                    </h4>
                                    <ul style={{ listStyle: 'none', padding: 0, display: 'flex', flexDirection: 'column', gap: 'var(--spacing-xs)' }}>
                                        {anomaly.reasons.map((reason, idx) => (
                                            <li key={idx} style={{ fontSize: '0.875rem', color: 'var(--text-primary)', paddingLeft: 'var(--spacing-md)', position: 'relative' }}>
                                                <span style={{ position: 'absolute', left: 0 }}>•</span>
                                                {reason}
                                            </li>
                                        ))}
                                    </ul>
                                </div>

                                {!anomaly.reviewed && (
                                    <button
                                        className="btn btn-primary"
                                        style={{ fontSize: '0.75rem' }}
                                        onClick={() => {
                                            // Review logic would go here
                                            console.log('Review anomaly:', anomaly.id);
                                        }}
                                    >
                                        Review Case
                                    </button>
                                )}
                            </div>
                        </div>
                    ))}

                    {anomalies.length === 0 && (
                        <div className="card" style={{ textAlign: 'center', padding: 'var(--spacing-2xl)' }}>
                            <p style={{ color: 'var(--text-secondary)' }}>
                                No anomalies found for selected filters
                            </p>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
