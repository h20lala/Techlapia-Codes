import React from 'react';

const Navigation = ({ onNavigate, activePage }) => {
    const styles = {
        container: {
            display: 'flex',
            flexDirection: 'column',
            gap: '6px',
            marginTop: 'auto',
        },
        button: {
            width: '100%',
            padding: '12px',
            borderRadius: '8px',
            border: 'none',
            background: '#475467',
            color: '#fff',
            fontWeight: '600',
            fontSize: '0.75rem',
            cursor: 'pointer',
            textTransform: 'uppercase',
            letterSpacing: '0.5px',
        },
        mainBtn: {
            background: '#1570EF' // Brighter blue for Main button distinction
        }
    };

    const renderBtn = (label, page, highlight = false) => (
        <button
            style={{ ...styles.button, ...(highlight ? styles.mainBtn : {}) }}
            onClick={() => onNavigate(page)}
        >
            {label}
        </button>
    );

    return (
        <div style={styles.container}>
            {/* Dashboard: Shows Settings & Logs */}
            {(activePage === 'dashboard' || !activePage) && (
                <>
                    {renderBtn('SETTINGS', 'settings')}
                    {renderBtn('LOG RECORDS', 'logs')}
                </>
            )}

            {/* Settings: Shows Main & Logs */}
            {activePage === 'settings' && (
                <>
                    {renderBtn('MAIN', 'dashboard', true)}
                    {renderBtn('LOG RECORDS', 'logs')}
                </>
            )}

            {/* Logs: Shows Main & Settings (User Request) */}
            {activePage === 'logs' && (
                <>
                    {renderBtn('MAIN', 'dashboard', true)}
                    {renderBtn('SETTINGS', 'settings')}
                </>
            )}
        </div>
    );
};

export default Navigation;
