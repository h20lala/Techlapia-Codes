import React from 'react';

const FeedingSchedule = () => {
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
        tableContainer: {
            background: '#1D2939',
            borderRadius: '8px',
            overflow: 'hidden',
            border: '1px solid #475467'
        },
        table: {
            width: '100%',
            borderCollapse: 'collapse',
            fontSize: '0.65rem', // Very compact text
            textAlign: 'center'
        },
        th: {
            color: '#98A2B3',
            padding: '6px 4px',
            borderBottom: '1px solid #475467',
            fontWeight: 'normal'
        },
        td: {
            padding: '6px 4px',
            borderBottom: '1px solid rgba(255,255,255,0.05)',
            color: '#fff'
        }
    };

    const schedule = [
        { date: '1/1/2026', time: '9:00 AM', feeds: '4 g', weight: '20 g' },
        { date: '1/1/2026', time: '12:00 PM', feeds: '4 g', weight: '20 g' },
        { date: '1/1/2026', time: '3:00 PM', feeds: '4 g', weight: '20 g' },
    ];

    return (
        <div style={styles.container}>
            <span style={styles.header}>Feeding Schedule</span>
            <div style={styles.tableContainer}>
                <table style={styles.table}>
                    <thead>
                        <tr>
                            <th style={styles.th}>Date</th>
                            <th style={styles.th}>Time</th>
                            <th style={styles.th}>Feeds</th>
                            <th style={styles.th}>Weight</th>
                        </tr>
                    </thead>
                    <tbody>
                        {schedule.map((row, i) => (
                            <tr key={i}>
                                <td style={styles.td}>{row.date}</td>
                                <td style={styles.td}>{row.time}</td>
                                <td style={styles.td}>{row.feeds}</td>
                                <td style={styles.td}>{row.weight}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default FeedingSchedule;
