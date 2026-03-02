import React from 'react';

const ActionButtons = ({ onFeederTriggered }) => {
    const handleFeeder = async () => {
        try {
            const res = await fetch(`http://${window.location.hostname}:5000/api/feed`, { method: 'POST' });
            if (res.ok && onFeederTriggered) {
                onFeederTriggered();
            }
        } catch (error) {
            console.error("Failed to trigger feeder", error);
        }
    };
    const styles = {
        container: {
            marginBottom: '8px'
        },
        header: {
            fontSize: '0.75rem',
            color: '#98A2B3',
            marginBottom: '4px',
            display: 'block',
        },
        grid: {
            display: 'grid',
            gridTemplateColumns: '1fr 1fr 1fr', // All in one row per Figure 10? 
            // Actually Figure 10 shows them stacked? No, Figure 9 shows override buttons.
            // Wait, Figure 10 (bottom right) shows Notifications.
            // Figure 9 (Page 18) shows Override section.
            // They look stacked vertically in the PDF image.
            // Let's keep them stacked but compact.
            gap: '8px',
        },
        rowStyles: {
            display: 'flex',
            flexDirection: 'column',
            gap: '6px'
        },
        button: {
            width: '100%',
            padding: '8px',
            borderRadius: '6px',
            border: 'none',
            color: '#fff',
            fontWeight: '600',
            fontSize: '0.65rem',
            cursor: 'pointer',
            textTransform: 'uppercase',
            letterSpacing: '0.5px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.2)'
        },
        waterBtn: { background: '#1570EF' }, // Blue
        aeratorBtn: { background: '#12B76A' }, // Green
        feederBtn: { background: '#F79009' }, // Orange
    };

    return (
        <div style={styles.container}>
            <span style={styles.header}>Override</span>
            <div style={styles.rowStyles}>
                <button style={{ ...styles.button, ...styles.waterBtn }}>WATER</button>
                <button style={{ ...styles.button, ...styles.aeratorBtn }}>AERATOR</button>
                <button style={{ ...styles.button, ...styles.feederBtn }} onClick={handleFeeder}>FEEDER</button>
            </div>
        </div>
    );
};

export default ActionButtons;
