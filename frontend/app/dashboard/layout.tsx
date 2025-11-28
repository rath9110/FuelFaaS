'use client';

import { ReactNode } from 'react';
import Sidebar from '../components/Sidebar';
import ProtectedRoute from '../components/ProtectedRoute';

export default function DashboardLayout({ children }: { children: ReactNode }) {
    return (
        <ProtectedRoute>
            <div style={{ display: 'flex', minHeight: '100vh' }}>
                <Sidebar />
                <main style={{
                    marginLeft: '256px',
                    flex: 1,
                    background: 'var(--bg-secondary)',
                    padding: 'var(--spacing-2xl)',
                    minHeight: '100vh'
                }}>
                    {children}
                </main>
            </div>
        </ProtectedRoute>
    );
}
