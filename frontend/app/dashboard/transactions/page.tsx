'use client';

import { useEffect, useState } from 'react';
import { FuelTransaction } from '../../types';
import { api } from '../../utils/api';

export default function TransactionsPage() {
    const [transactions, setTransactions] = useState<FuelTransaction[]>([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('');

    useEffect(() => {
        fetchTransactions();
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

    const filteredTransactions = transactions.filter(tx =>
        tx.transaction_id.toLowerCase().includes(filter.toLowerCase()) ||
        tx.vehicle_id.toLowerCase().includes(filter.toLowerCase())
    );

    return (
        <div>
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
        </div>
    );
}
