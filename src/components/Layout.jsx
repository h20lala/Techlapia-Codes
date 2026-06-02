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
            display: 'flex',
            flexWrap: 'wrap',
            minHeight: '100vh',
            gap: 'var(--spacing-md)',
            padding: 'var(--spacing-md)',
            background: 'var(--color-primary)',
        },
        mainArea: {
            flex: '1 1 400px', // Take remaining space, wrap if < 400px
            minHeight: '400px', // Prevent camera from collapsing too much
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
            flex: '1 1 340px', // Allow to grow on small screens, wrap if < 340px
            maxWidth: '100%', // Prevent overflow on very small screens
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
