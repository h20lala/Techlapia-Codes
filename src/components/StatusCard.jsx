import React from 'react';
import '../styles/global.css';

/**
 * StatusCard Component
 * Displays a single metric with a status indicator color.
 * 
 * @param {string} label - The label for the metric (e.g., "Temperature")
 * @param {string} value - The value to display (e.g., "25° C")
 * @param {string} status - 'Normal', 'Warning', 'Critical' (determines color)
 * @param {string} subtext - Optional subtext (e.g., "| Normal")
 */
const StatusCard = ({ label, value, status = 'Normal', subtext }) => {
    const getStatusColor = (s) => {
        switch (s.toLowerCase()) {
            case 'warning': return 'var(--color-warning)';
            case 'critical': return 'var(--color-error)';
            case 'high': return 'var(--color-error)';
            case 'low': return 'var(--color-warning)';
            default: return 'var(--color-info)'; // Default is blue/info
        }
    };

    const styles = {
        card: {
            background: 'var(--color-secondary)',
            padding: 'var(--spacing-md)',
            borderRadius: 'var(--radius-md)',
            borderLeft: `4px solid ${getStatusColor(status)}`,
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            /* Glassmorphism effect */
            boxShadow: 'var(--shadow-sm)',
        },
        label: {
            fontSize: '0.85rem',
            color: 'var(--color-text-muted)',
            marginBottom: '4px',
        },
        value: {
            fontSize: '1.25rem',
            fontWeight: '600',
            color: 'var(--color-text-main)',
        },
        subtext: {
            fontSize: '0.75rem',
            color: getStatusColor(status),
            marginLeft: '6px'
        }
    };

    return (
        <div style={styles.card}>
            <span style={styles.label}>{label}</span>
            <div style={{ display: 'flex', alignItems: 'baseline' }}>
                <span style={styles.value}>{value}</span>
                {subtext && <span style={styles.subtext}>{subtext}</span>}
            </div>
        </div>
    );
};

export default StatusCard;
