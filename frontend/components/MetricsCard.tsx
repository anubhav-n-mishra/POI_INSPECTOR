'use client';

import { ReactNode } from 'react';

interface MetricsCardProps {
    label: string;
    value: string;
    description: string;
    status: 'good' | 'fair' | 'poor';
    icon: ReactNode;
}

export default function MetricsCard({ label, value, description, status, icon }: MetricsCardProps) {
    const getStatusColor = () => {
        switch (status) {
            case 'good': return 'var(--google-green)';
            case 'fair': return '#ea8600';
            case 'poor': return 'var(--google-red)';
        }
    };

    const getBadgeClass = () => {
        switch (status) {
            case 'good': return 'badge-success';
            case 'fair': return 'badge-warning';
            case 'poor': return 'badge-error';
        }
    };

    return (
        <div className="material-card elevation-1">
            <div style={{ display: 'flex', alignItems: 'start', justifyContent: 'space-between', marginBottom: '16px' }}>
                <div style={{ width: '40px', height: '40px', background: 'rgba(26, 115, 232, 0.08)', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: getStatusColor() }}>
                    {icon}
                </div>
                <span className={`material-badge ${getBadgeClass()}`} style={{ fontSize: '10px' }}>
                    {status.toUpperCase()}
                </span>
            </div>

            <div className="headline-medium" style={{ marginBottom: '4px', color: getStatusColor() }}>
                {value}
            </div>
            <div className="title-medium" style={{ marginBottom: '4px' }}>{label}</div>
            <div className="body-medium" style={{ color: 'var(--on-surface-variant)', fontSize: '12px' }}>{description}</div>
        </div>
    );
}
