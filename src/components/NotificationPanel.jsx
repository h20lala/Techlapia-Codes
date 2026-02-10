import React from 'react';

const NotificationPanel = () => {
    const styles = {
        container: {
            marginBottom: '4px'
        },
        header: {
            fontSize: '0.75rem',
            color: '#98A2B3',
            marginBottom: '4px',
            display: 'block',
        },
        box: {
            background: '#1D2939',
            borderRadius: '8px',
            padding: '12px',
            textAlign: 'center',
            border: '1px solid #475467', // Subtle border
            minHeight: '60px', // Compact
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            alignItems: 'center'
        },
        title: {
            fontSize: '0.65rem',
            textTransform: 'uppercase',
            letterSpacing: '0.5px',
            marginBottom: '2px',
            color: '#fff'
        },
        message: {
            fontSize: '0.75rem',
            fontWeight: 'bold',
            color: '#66C2FF' // Light blue highlight
        }
    };

    return (
        <div style={styles.container}>
            <span style={styles.header}>Notification</span>
            <div style={styles.box}>
                <div style={styles.title}>ALL WATER QUALITY</div>
                <div style={styles.message}>WITHIN NORMAL RANGE</div>
            </div>
        </div>
    );
};

export default NotificationPanel;
