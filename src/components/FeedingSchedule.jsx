import React, { useState, useEffect } from 'react';

const FeedingSchedule = ({ refreshTrigger }) => {
    const [schedule, setSchedule] = useState([]);

    useEffect(() => {
        const fetchSchedule = async () => {
            try {
                // Fetch historical logs instead of future schedule
                const res = await fetch(`http://${window.location.hostname}:5000/api/logs`);
                if (res.ok) {
                    const data = await res.json();
                    setSchedule(data); // `data` is now an array of logs
                }
            } catch (err) {
                console.error("Error fetching schedule:", err);
            }
        };
        fetchSchedule();
        const interval = setInterval(fetchSchedule, 60000); // 1 minute refresh
        return () => clearInterval(interval);
    }, [refreshTrigger]);
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
            overflowY: 'auto',
            maxHeight: '80px', // Set max height to show ~2 items + header
            border: '1px solid #475467'
        },
        table: {
            width: '100%',
            borderCollapse: 'collapse',
            fontSize: '0.65rem',
            textAlign: 'center'
        },
        th: {
            color: '#98A2B3',
            padding: '6px 4px',
            borderBottom: '1px solid #475467',
            fontWeight: 'normal',
            position: 'sticky',
            top: 0,
            background: '#1D2939', // Match container background for sticky header
            zIndex: 1
        },
        td: {
            padding: '6px 4px',
            borderBottom: '1px solid rgba(255,255,255,0.05)',
            color: '#fff'
        }
    };

    // removed hardcoded map

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
                                <td style={styles.td}>{row.date_val}</td>
                                <td style={styles.td}>{row.time_val}</td>
                                <td style={styles.td}>{row.feed}</td>
                                <td style={styles.td}>{row.w}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default FeedingSchedule;
