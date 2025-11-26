'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../contexts/AuthContext';

export default function LoginPage() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const { login } = useAuth();
    const router = useRouter();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setIsLoading(true);

        try {
            await login(username, password);
            router.push('/dashboard');
        } catch (err: any) {
            setError(err.message || 'Login failed. Please check your credentials.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div style={{
            minHeight: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'linear-gradient(135deg, var(--primary-600) 0%, var(--primary-800) 100%)',
            padding: 'var(--spacing-lg)'
        }}>
            <div style={{
                width: '100%',
                maxWidth: '420px',
                background: 'var(--bg-primary)',
                borderRadius: 'var(--radius-lg)',
                padding: 'var(--spacing-2xl)',
                boxShadow: '0 20px 60px rgba(0, 0, 0, 0.3)'
            }}>
                {/* Logo */}
                <div style={{ textAlign: 'center', marginBottom: 'var(--spacing-2xl)' }}>
                    <h1 style={{
                        fontSize: '2rem',
                        fontWeight: '700',
                        color: 'var(--primary-600)',
                        marginBottom: 'var(--spacing-xs)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        gap: 'var(--spacing-sm)'
                    }}>
                        <span>⛽</span>
                        FuelGuard AI
                    </h1>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
                        Sign in to your account
                    </p>
                </div>

                {/* Error Message */}
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

                {/* Login Form */}
                <form onSubmit={handleSubmit}>
                    <div style={{ marginBottom: 'var(--spacing-lg)' }}>
                        <label style={{
                            display: 'block',
                            marginBottom: 'var(--spacing-xs)',
                            fontSize: '0.875rem',
                            fontWeight: '500',
                            color: 'var(--text-primary)'
                        }}>
                            Username
                        </label>
                        <input
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            required
                            style={{
                                width: '100%',
                                padding: 'var(--spacing-sm) var(--spacing-md)',
                                border: '1px solid var(--border-color)',
                                borderRadius: 'var(--radius-md)',
                                fontSize: '1rem',
                                background: 'var(--bg-secondary)',
                                color: 'var(--text-primary)',
                                transition: 'all var(--transition-fast)'
                            }}
                            onFocus={(e) => e.target.style.borderColor = 'var(--primary-500)'}
                            onBlur={(e) => e.target.style.borderColor = 'var(--border-color)'}
                            placeholder="Enter your username"
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
                            Password
                        </label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            style={{
                                width: '100%',
                                padding: 'var(--spacing-sm) var(--spacing-md)',
                                border: '1px solid var(--border-color)',
                                borderRadius: 'var(--radius-md)',
                                fontSize: '1rem',
                                background: 'var(--bg-secondary)',
                                color: 'var(--text-primary)',
                                transition: 'all var(--transition-fast)'
                            }}
                            onFocus={(e) => e.target.style.borderColor = 'var(--primary-500)'}
                            onBlur={(e) => e.target.style.borderColor = 'var(--border-color)'}
                            placeholder="Enter your password"
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={isLoading}
                        style={{
                            width: '100%',
                            padding: 'var(--spacing-md)',
                            background: isLoading ? 'var(--text-tertiary)' : 'var(--primary-600)',
                            color: 'white',
                            border: 'none',
                            borderRadius: 'var(--radius-md)',
                            fontSize: '1rem',
                            fontWeight: '600',
                            cursor: isLoading ? 'not-allowed' : 'pointer',
                            transition: 'all var(--transition-fast)'
                        }}
                        onMouseEnter={(e) => {
                            if (!isLoading) e.currentTarget.style.background = 'var(--primary-700)';
                        }}
                        onMouseLeave={(e) => {
                            if (!isLoading) e.currentTarget.style.background = 'var(--primary-600)';
                        }}
                    >
                        {isLoading ? 'Signing in...' : 'Sign In'}
                    </button>
                </form>

                {/* Demo Credentials */}
                <div style={{
                    marginTop: 'var(--spacing-xl)',
                    padding: 'var(--spacing-md)',
                    background: 'var(--bg-secondary)',
                    borderRadius: 'var(--radius-md)',
                    textAlign: 'center'
                }}>
                    <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: 'var(--spacing-xs)' }}>
                        Demo Credentials
                    </p>
                    <p style={{ fontSize: '0.875rem', color: 'var(--text-primary)', fontFamily: 'monospace' }}>
                        admin / admin123
                    </p>
                </div>
            </div>
        </div>
    );
}
