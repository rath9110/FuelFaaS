'use client';

import { AnomalyResult } from '../types';

interface SeverityBadgeProps {
    severity: AnomalyResult['severity'];
}

export default function SeverityBadge({ severity }: SeverityBadgeProps) {
    const getBadgeClass = () => {
        switch (severity) {
            case 'Critical':
                return 'badge-critical';
            case 'High':
                return 'badge-high';
            case 'Medium':
                return 'badge-medium';
            case 'Low':
                return 'badge-low';
            default:
                return 'badge-low';
        }
    };

    return <span className={`badge ${getBadgeClass()}`}>{severity}</span>;
}
