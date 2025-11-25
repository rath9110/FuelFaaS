'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: '📊' },
    { name: 'Transactions', href: '/dashboard/transactions', icon: '⛽' },
    { name: 'Anomalies', href: '/dashboard/anomalies', icon: '🚨' },
    { name: 'Vehicles', href: '/dashboard/vehicles', icon: '🚗' },
];

export default function Sidebar() {
    const pathname = usePathname();

    return (
        <aside style={{
            width: '256px',
            height: '100vh',
            background: 'var(--bg-primary)',
            borderRight: '1px solid var(--border-color)',
            padding: 'var(--spacing-lg)',
            position: 'fixed',
            left: 0,
            top: 0,
            display: 'flex',
            flexDirection: 'column',
            gap: 'var(--spacing-md)'
        }}>
            {/* Logo */}
            <div style={{ marginBottom: 'var(--spacing-xl)' }}>
                <h1 style={{
                    fontSize: '1.5rem',
                    fontWeight: '700',
                    color: 'var(--primary-600)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 'var(--spacing-sm)'
                }}>
                    <span>⛽</span>
                    FuelGuard AI
                </h1>
            </div>

            {/* Navigation */}
            <nav style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-xs)' }}>
                {navigation.map((item) => {
                    const isActive = pathname === item.href;
                    return (
                        <Link
                            key={item.name}
                            href={item.href}
                            style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: 'var(--spacing-sm)',
                                padding: 'var(--spacing-sm) var(--spacing-md)',
                                borderRadius: 'var(--radius-md)',
                                fontSize: '0.875rem',
                                fontWeight: '500',
                                color: isActive ? 'var(--primary-600)' : 'var(--text-secondary)',
                                background: isActive ? 'rgba(249, 115, 22, 0.1)' : 'transparent',
                                transition: 'all var(--transition-fast)',
                                textDecoration: 'none'
                            }}
                            onMouseEnter={(e) => {
                                if (!isActive) {
                                    e.currentTarget.style.background = 'var(--bg-tertiary)';
                                }
                            }}
                            onMouseLeave={(e) => {
                                if (!isActive) {
                                    e.currentTarget.style.background = 'transparent';
                                }
                            }}
                        >
                            <span style={{ fontSize: '1.25rem' }}>{item.icon}</span>
                            {item.name}
                        </Link>
                    );
                })}
            </nav>
        </aside>
    );
}
