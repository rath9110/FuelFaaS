'use client';

import { useEffect, useState } from 'react';
import { FuelTransaction } from '../../types';
import { api } from '../../utils/api';
import AddProviderModal from './AddProviderModal';

export default function TransactionsPage() {
    const [transactions, setTransactions] = useState<FuelTransaction[]>([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('');
    const [showAddProvider, setShowAddProvider] = useState(false);
    const [providers, setProviders] = useState<any[]>([]);
    const [isSyncing, setIsSyncing] = useState(false);

    useEffect(() => {
        fetchTransactions();
        fetchProviders();
    }, []);

    const fetchTransactions = async () => {
        try {
            const data = await api.getTransactions({ limit: 100 });
            setTransactions(data);
        } catch (error) {
            console.error('Error fetching transactions:', error);
        } finally {
            setLoading(false);
        }
    };

    const fetchProviders = async () => {
        try {
            const data = await api.getProviderCredentials();
            setProviders(data);
        } catch (error) {
            console.error('Error fetching providers:', error);
        }
    };

    const handleSync = async (providerName?: string) => {
        setIsSyncing(true);
        try {
            if (providerName) {
                await api.syncProvider(providerName);
            } else {
                await api.syncAllProviders();
            }
            await fetchTransactions();
            alert('Sync completed successfully!');
        } catch (error: any) {
            alert('Sync failed: ' + (error.message || 'Unknown error'));
        } finally {
            setIsSyncing(false);
        }
    };

    const handleDeleteProvider = async (credentialId: number) => {
        if (!confirm('Are you sure you want to delete this provider?')) return;

        try {
            await api.deleteProviderCredential(credentialId);
            await fetchProviders();
        } catch (error: any) {
            alert('Delete failed: ' + (error.message || 'Unknown error'));
        }
    };

    const filteredTransactions = transactions.filter(tx =>
        tx.transaction_id.toLowerCase().includes(filter.toLowerCase()) ||
        tx.vehicle_id.toLowerCase().includes(filter.toLowerCase())
    );

    return (
        <div>
            {/* Provider Management Section */}
            <div className="card" style={{ marginBottom: 'var(--spacing-xl)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--spacing-lg)' }}>
                    <h2 style={{ fontSize: '1.25rem', fontWeight: '700', color: 'var(--text-primary)' }}>
                        Fuel Card Providers
                    </h2>
                    <button
                        onClick={() => setShowAddProvider(true)}
                        style={{
                            padding: 'var(--spacing-sm) var(--spacing-lg)',
                            background: 'var(--primary-600)',
                            color: 'white',
                            border: 'none',
                            borderRadius: 'var(--radius-md)',
                            fontSize: '0.875rem',
                            fontWeight: '600',
                            cursor: 'pointer'
                        }}
                    >
                        + Add Provider
                    </button>
                </div>

                {providers.length === 0 ? (
                    <div style={{
                        textAlign: 'center',
                        padding: 'var(--spacing-2xl)',
                        color: 'var(--text-secondary)'
                    }}>
                        <p>No providers configured yet.</p>
                        <p style={{ fontSize: '0.875rem', marginTop: 'var(--spacing-sm)' }}>
                            Add a fuel card provider to start syncing transactions automatically.
                        </p>
                    </div>
                ) : (
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', gap: 'var(--spacing-md)' }}>
                        {providers.map((provider) => (
                            <div
                                key={provider.id}
                                style={{
                                    padding: 'var(--spacing-lg)',
                                    background: 'var(--bg-secondary)',
                                    borderRadius: 'var(--radius-md)',
                                    border: '1px solid var(--border-color)'
                                }}
                            >
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: 'var(--spacing-md)' }}>
                                    <div>
                                        <h3 style={{
                                            fontSize: '1rem',
                                            fontWeight: '600',
                                            textTransform: 'uppercase',
                                            color: 'var(--text-primary)',
                                            marginBottom: 'var(--spacing-xs)'
                                        }}>
                                            {provider.provider_name}
                                        </h3>
                                        <span className={`badge ${provider.is_active ? 'badge-success' : 'badge-error'}`}>
                                            {provider.is_active ? 'Active' : 'Inactive'}
                                        </span>
                                    </div>
                                    <button
                                        onClick={() => handleDeleteProvider(provider.id)}
                                        style={{
                                            background: 'none',
                                            border: 'none',
                                            color: 'var(--danger)',
                                            cursor: 'pointer',
                                            fontSize: '1.25rem'
                                        }}
                                        title="Delete provider"
                                    >
                                        Delete
                                    </button>
                                </div>
                                <button
                                    onClick={() => handleSync(provider.provider_name)}
                                    disabled={isSyncing}
                                    style={{
                                        width: '100%',
                                        padding: 'var(--spacing-sm)',
                                        background: isSyncing ? 'var(--text-tertiary)' : 'var(--primary-600)',
                                        color: 'white',
                                        border: 'none',
                                        borderRadius: 'var(--radius-md)',
                                        fontSize: '0.875rem',
                                        fontWeight: '600',
                                        cursor: isSyncing ? 'not-allowed' : 'pointer'
                                    }}
                                >
                                    {isSyncing ? 'Syncing...' : 'Sync Now'}
                                </button>
                            </div>
                        ))}
                    </div>
                )}

                {providers.length > 0 && (
                    <button
                        onClick={() => handleSync()}
                        disabled={isSyncing}
                        style={{
                            marginTop: 'var(--spacing-lg)',
                            padding: 'var(--spacing-md) var(--spacing-xl)',
                            background: isSyncing ? 'var(--text-tertiary)' : 'var(--success)',
                            color: 'white',
                            border: 'none',
                            borderRadius: 'var(--radius-md)',
                            fontSize: '0.875rem',
                            fontWeight: '600',
                            cursor: isSyncing ? 'not-allowed' : 'pointer'
                        }}
                    >
                        {isSyncing ? 'Syncing All...' : 'Sync All Providers'}
                    </button>
                )}
            </div>

            {/* Transactions List */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--spacing-xl)' }}>
                <h1 style={{ fontSize: '2rem', fontWeight: '700', color: 'var(--text-primary)' }}>
                    Fuel Transactions
                </h1>
                <input
                    type="text"
                    placeholder="Search transactions..."
                    value={filter}
                    onChange={(e) => setFilter(e.target.value)}
                    style={{
                        padding: 'var(--spacing-sm) var(--spacing-md)',
                        borderRadius: 'var(--radius-md)',
                        border: '1px solid var(--border-color)',
                        fontSize: '0.875rem',
                        width: '300px'
                    }}
                />
            </div>

            {loading ? (
                <div style={{ display: 'flex', justifyContent: 'center', padding: 'var(--spacing-2xl)' }}>
                    <div className="spinner" />
                </div>
            ) : (
                <div className="card" style={{ overflow: 'auto' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                        <thead>
                            <tr style={{ borderBottom: '2px solid var(--border-color)' }}>
                                <th style={{ padding: 'var(--spacing-md)', textAlign: 'left', fontWeight: '600', color: 'var(--text-secondary)' }}>ID</th>
                                <th style={{ padding: 'var(--spacing-md)', textAlign: 'left', fontWeight: '600', color: 'var(--text-secondary)' }}>Vehicle</th>
                                <th style={{ padding: 'var(--spacing-md)', textAlign: 'left', fontWeight: '600', color: 'var(--text-secondary)' }}>Provider</th>
                                <th style={{ padding: 'var(--spacing-md)', textAlign: 'left', fontWeight: '600', color: 'var(--text-secondary)' }}>Liters</th>
                                <th style={{ padding: 'var(--spacing-md)', textAlign: 'left', fontWeight: '600', color: 'var(--text-secondary)' }}>Amount</th>
                                <th style={{ padding: 'var(--spacing-md)', textAlign: 'left', fontWeight: '600', color: 'var(--text-secondary)' }}>Date</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filteredTransactions.map((tx) => (
                                <tr key={tx.id} style={{ borderBottom: '1px solid var(--border-color)' }}>
                                    <td style={{ padding: 'var(--spacing-md)', fontFamily: 'monospace' }}>{tx.transaction_id}</td>
                                    <td style={{ padding: 'var(--spacing-md)' }}>{tx.vehicle_id}</td>
                                    <td style={{ padding: 'var(--spacing-md)' }}>
                                        <span className="badge" style={{ textTransform: 'uppercase' }}>{tx.provider}</span>
                                    </td>
                                    <td style={{ padding: 'var(--spacing-md)' }}>{tx.liters.toFixed(1)}L</td>
                                    <td style={{ padding: 'var(--spacing-md)', fontWeight: '600' }}>{tx.total_amount.toFixed(2)} SEK</td>
                                    <td style={{ padding: 'var(--spacing-md)', color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
                                        {new Date(tx.timestamp).toLocaleString()}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                    {filteredTransactions.length === 0 && (
                        <p style={{ textAlign: 'center', padding: 'var(--spacing-2xl)', color: 'var(--text-secondary)' }}>
                            No transactions found
                        </p>
                    )}
                </div>
            )}

            {/* Add Provider Modal */}
            {showAddProvider && (
                <AddProviderModal
                    onClose={() => setShowAddProvider(false)}
                    onSuccess={() => {
                        fetchProviders();
                        fetchTransactions();
                    }}
                />
            )}
        </div>
    );
}
