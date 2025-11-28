'use client';

import { useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { useAuth } from '../contexts/AuthContext';

export default function ProtectedRoute({ children }: { children: React.ReactNode }) {
    const { user, isLoading } = useAuth();
    const router = useRouter();
    const pathname = usePathname();

    useEffect(() => {
        // Don't redirect if we're already on the login page
        if (pathname === '/login') {
            return;
        }

        // Wait for auth to load
        if (isLoading) {
            return;
        }

        // Redirect to login if not authenticated
        if (!user) {
            router.push('/login');
        }
    }, [user, isLoading, pathname, router]);

    // Show loading spinner while checking auth
    if (isLoading) {
        return (
            <div style={{
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                height: '100vh',
                width: '100vw'
            }}>
                <div className="spinner" />
            </div>
        );
    }

    // Don't render children if not authenticated
    if (!user && pathname !== '/login') {
        return null;
    }

    return <>{children}</>;
}
