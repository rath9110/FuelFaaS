'use client';

import { useState } from 'react';
import { api } from '../../utils/api';

interface ProviderModalProps {
    onClose: () => void;
    onSuccess: () => void;
}

export default function AddProviderModal({ onClose, onSuccess }: ProviderModalProps) {
    const [selectedProvider, setSelectedProvider] = useState('okq8');
    const [clientId, setClientId] = useState('');
    const [clientSecret, setClientSecret] = useState('');
    const [cardId, setCardId] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [error, setError] = useState('');

    const providers = [
        { value: 'okq8', label: 'OKQ8', icon: '🛢️' },
        { value: 'preem', label: 'Preem', icon: '⛽' },
        { value: 'shell', label: 'Shell', icon: '🐚' },
        { value: 'circlek', label: 'Circle K', icon: '🔴' }
    ];

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setIsSubmitting(true);

        try {
            await api.addProviderCredential(selectedProvider, {
                client_id: clientId,
                client_secret: clientSecret,
                card_id: cardId
            });

            onSuccess();
            onClose();
        } catch (err: any) {
            setError(err.message || 'Failed to add provider');
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0, 0, 0, 0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000
        }}>
            <div style={{
                background: 'var(--bg-primary)',
                borderRadius: 'var(--radius-lg)',
                padding: 'var(--spacing-2xl)',
                maxWidth: '500px',
                width: '100%',
                maxHeight: '90vh',
                overflow: 'auto'
            }}>
                <div style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    marginBottom: 'var(--spacing-xl)'
                }}>
                    <h2 style={{ fontSize: '1.5rem', fontWeight: '700', color: 'var(--text-primary)' }}>
                        Add Fuel Card Provider
                    </h2>
                    <button
                        onClick={onClose}
                        style={{
                            background: 'none',
                            border: 'none',
                            fontSize: '1.5rem',
                            cursor: 'pointer',
                            color: 'var(--text-secondary)'
                        }}
                    >
                        ×
                    </button>
                </div>

                {error && (
                    <div style={{
                        padding: 'var(--spacing-md)',
                        background: 'rgba(239, 68, 68, 0.1)',
                        border: '1px solid rgba(239, 68, 68, 0.3)',
                        borderRadius: 'var(--radius-md)',
                        marginBottom: 'var(--spacing-lg)',
                        color: '#ef4444'
                    }}>
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit}>
                    <div style={{ marginBottom: 'var(--spacing-lg)' }}>
                        <label style={{
                            display: 'block',
                            marginBottom: 'var(--spacing-sm)',
                            fontSize: '0.875rem',
                            fontWeight: '600',
                            color: 'var(--text-primary)'
                        }}>
                            Select Provider
                        </label>
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 'var(--spacing-md)' }}>
                            {providers.map(provider => (
                                <button
                                    key={provider.value}
                                    type="button"
                                    onClick={() => setSelectedProvider(provider.value)}
                                    style={{
                                        padding: 'var(--spacing-md)',
                                        border: selectedProvider === provider.value
                                            ? '2px solid var(--primary-600)'
                                            : '1px solid var(--border-color)',
                                        borderRadius: 'var(--radius-md)',
                                        background: selectedProvider === provider.value
                                            ? 'rgba(99, 102, 241, 0.1)'
                                            : 'var(--bg-secondary)',
                                        cursor: 'pointer',
                                        display: 'flex',
                                        flexDirection: 'column',
                                        alignItems: 'center',
                                        gap: 'var(--spacing-xs)',
                                        transition: 'all var(--transition-fast)'
                                    }}
                                >
                                    <span style={{ fontSize: '2rem' }}>{provider.icon}</span>
                                    <span style={{
                                        fontSize: '0.875rem',
                                        fontWeight: '600',
                                        color: selectedProvider === provider.value ? 'var(--primary-600)' : 'var(--text-primary)'
                                    }}>
                                        {provider.label}
                                    </span>
                                </button>
                            ))}
                        </div>
                    </div>

                    <div style={{ marginBottom: 'var(--spacing-lg)' }}>
                        <label style={{
                            display: 'block',
                            marginBottom: 'var(--spacing-xs)',
                            fontSize: '0.875rem',
                            fontWeight: '500',
                            color: 'var(--text-primary)'
                        }}>
                            Client ID
                        </label>
                        <input
                            type="text"
                            value={clientId}
                            onChange={(e) => setClientId(e.target.value)}
                            required
                            style={{
                                width: '100%',
                                padding: 'var(--spacing-sm) var(--spacing-md)',
                                border: '1px solid var(--border-color)',
                                borderRadius: 'var(--radius-md)',
                                fontSize: '0.875rem',
                                background: 'var(--bg-secondary)',
                                color: 'var(--text-primary)'
                            }}
                            placeholder="Enter client ID"
                        />
                    </div>

                    <div style={{ marginBottom: 'var(--spacing-lg)' }}>
                        <label style={{
                            display: 'block',
                            marginBottom: 'var(--spacing-xs)',
                            fontSize: '0.875rem',
                            fontWeight: '500',
                            color: 'var(--text-primary)'
                        }}>
                            Client Secret
                        </label>
                        <input
                            type="password"
                            value={clientSecret}
                            onChange={(e) => setClientSecret(e.target.value)}
                            required
                            style={{
                                width: '100%',
                                padding: 'var(--spacing-sm) var(--spacing-md)',
                                border: '1px solid var(--border-color)',
                                borderRadius: 'var(--radius-md)',
                                fontSize: '0.875rem',
                                background: 'var(--bg-secondary)',
                                color: 'var(--text-primary)'
                            }}
                            placeholder="Enter client secret"
                        />
                    </div>

                    <div style={{ marginBottom: 'var(--spacing-xl)' }}>
                        <label style={{
                            display: 'block',
                            marginBottom: 'var(--spacing-xs)',
                            fontSize: '0.875rem',
                            fontWeight: '500',
                            color: 'var(--text-primary)'
                        }}>
                            Card ID
                        </label>
                        <input
                            type="text"
                            value={cardId}
                            onChange={(e) => setCardId(e.target.value)}
                            required
                            style={{
                                width: '100%',
                                padding: 'var(--spacing-sm) var(--spacing-md)',
                                border: '1px solid var(--border-color)',
                                borderRadius: 'var(--radius-md)',
                                fontSize: '0.875rem',
                                background: 'var(--bg-secondary)',
                                color: 'var(--text-primary)'
                            }}
                            placeholder="Enter card ID"
                        />
                    </div>

                    <div style={{ display: 'flex', gap: 'var(--spacing-md)' }}>
                        <button
                            type="button"
                            onClick={onClose}
                            style={{
                                flex: 1,
                                padding: 'var(--spacing-md)',
                                border: '1px solid var(--border-color)',
                                borderRadius: 'var(--radius-md)',
                                background: 'transparent',
                                color: 'var(--text-primary)',
                                fontSize: '0.875rem',
                                fontWeight: '600',
                                cursor: 'pointer'
                            }}
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            disabled={isSubmitting}
                            style={{
                                flex: 1,
                                padding: 'var(--spacing-md)',
                                border: 'none',
                                borderRadius: 'var(--radius-md)',
                                background: isSubmitting ? 'var(--text-tertiary)' : 'var(--primary-600)',
                                color: 'white',
                                fontSize: '0.875rem',
                                fontWeight: '600',
                                cursor: isSubmitting ? 'not-allowed' : 'pointer'
                            }}
                        >
                            {isSubmitting ? 'Adding...' : 'Add Provider'}
                        </button>
                    </div>
                </form>

                <div style={{
                    marginTop: 'var(--spacing-xl)',
                    padding: 'var(--spacing-md)',
                    background: 'var(--bg-secondary)',
                    borderRadius: 'var(--radius-md)',
                    fontSize: '0.75rem',
                    color: 'var(--text-secondary)'
                }}>
                    <strong>Note:</strong> For demo purposes, you can use any test credentials. The system will validate and store them securely.
                </div>
            </div>
        </div>
    );
}
