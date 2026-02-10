import React from 'react';

/**
 * Layout Component
 * Provides the main structure: 
 * Left side: Camera Feed / Main Content
 * Right side: Sidebar / Controls
 */
const Layout = ({ children, sidebar }) => {
    const styles = {
        container: {
            display: 'grid',
            gridTemplateColumns: '1fr 340px', // Camera takes remaining space, sidebar fixed width
            height: '100vh',
            gap: 'var(--spacing-md)',
            padding: 'var(--spacing-md)',
            background: 'var(--color-primary)',
        },
        mainArea: {
            background: 'var(--color-text-main)', // Placeholder for camera feed (white for now)
            borderRadius: 'var(--radius-lg)',
            overflow: 'hidden',
            position: 'relative',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#000', // Text on white bg
        },
        sidebarArea: {
            display: 'flex',
            flexDirection: 'column',
            gap: 'var(--spacing-md)',
            overflowY: 'auto',
        }
    };

    return (
        <div style={styles.container}>
            <main style={styles.mainArea}>
                {children}
            </main>
            <aside style={styles.sidebarArea}>
                {sidebar}
            </aside>
        </div>
    );
};

export default Layout;
