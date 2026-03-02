import React, { useState, useEffect } from 'react';
import Navigation from '../components/Navigation.jsx';
import Layout from '../components/Layout.jsx';
import jsPDF from 'jspdf';
import 'jspdf-autotable';

const LogRecords = ({ onNavigate }) => {
    const [currentTime, setCurrentTime] = useState(new Date());

    // Real-time Clock
    useEffect(() => {
        const timer = setInterval(() => setCurrentTime(new Date()), 1000);
        return () => clearInterval(timer);
    }, []);

    const [logs, setLogs] = useState([]);

    useEffect(() => {
        const fetchLogs = async () => {
            try {
                const res = await fetch(`http://${window.location.hostname}:5000/api/logs`);
                if (res.ok) {
                    const data = await res.json();
                    setLogs(data);
                }
            } catch (err) {
                console.error("Error fetching logs:", err);
            }
        };
        fetchLogs();
        const interval = setInterval(fetchLogs, 5000); // 5 sec refresh
        return () => clearInterval(interval);
    }, []);

    const [selectedId, setSelectedId] = useState(null);

    const handleSavePDF = () => {
        const doc = new jsPDF();
        doc.text("Techlapia Log Records", 14, 15);

        const tableColumn = ["Date", "Length", "Feed", "Weight", "Pop", "Temp", "pH", "Lvl", "Turb"];
        const tableRows = logs.map(log => [
            log.date, log.len, log.feed, log.w, log.pop, log.temp, log.ph, log.lvl, log.turb
        ]);

        doc.autoTable({
            head: [tableColumn],
            body: tableRows,
            startY: 20,
        });

        doc.save("techlapia_logs.pdf");
    };

    const handleDelete = async () => {
        if (selectedId) {
            try {
                await fetch(`http://${window.location.hostname}:5000/api/logs/${selectedId}`, { method: 'DELETE' });
                setLogs(logs.filter(log => log.id !== selectedId));
                setSelectedId(null);
            } catch (err) {
                console.error("Error deleting log:", err);
            }
        }
    };

    const styles = {
        sidebarContainer: {
            display: 'flex', flexDirection: 'column', gap: '8px', height: '100%'
        },
        header: {
            background: '#1D2939', color: '#fff', padding: '10px',
            borderRadius: '8px', marginBottom: '4px',
            display: 'flex', justifyContent: 'space-between', alignItems: 'center'
        },
        logoText: {
            fontSize: '1.2rem', fontWeight: 'bold', fontFamily: 'var(--font-family-display)'
        },
        date: { fontSize: '0.65rem', color: 'var(--color-text-muted)' },
        clockContainer: { textAlign: 'right' },

        // Table Styles
        tableContainer: {
            width: '100%', height: '100%', overflow: 'auto',
            borderRadius: 'var(--radius-lg)',
            padding: '0',
        },
        table: {
            width: '100%',
            borderCollapse: 'collapse',
            fontSize: '0.8rem',
            textAlign: 'center'
        },
        th: {
            padding: '10px 4px',
            background: '#101828',
            color: '#fff',
            borderBottom: '2px solid #e4e7ec',
            fontWeight: 'normal',
            position: 'sticky', top: 0,
            fontSize: '0.75rem'
        },
        td: {
            padding: '8px 4px',
            borderBottom: '1px solid #e4e7ec',
            cursor: 'pointer',
            fontSize: '0.75rem',
            color: '#101828'
        },
        selectedRow: {
            background: '#e0f2fe'
        },

        actionBtn: {
            padding: '12px',
            borderRadius: '8px',
            border: 'none',
            color: '#fff',
            fontWeight: 'bold',
            cursor: 'pointer',
            textAlign: 'center',
            textTransform: 'uppercase',
            fontSize: '0.75rem',
            marginBottom: '4px',
            width: '100%'
        },
        saveBtn: { background: '#12B76A' },
        deleteBtn: { background: '#F04438' },
    };

    return (
        <Layout
            sidebar={
                <div style={styles.sidebarContainer}>
                    {/* Logo Section with Clock */}
                    <div style={styles.header}>
                        <div style={styles.logoText}>TECHLAPIA</div>
                        <div style={styles.clockContainer}>
                            <div style={{ fontSize: '0.7rem', fontWeight: 'bold' }}>
                                {currentTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            </div>
                            <div style={styles.date}>
                                {currentTime.toLocaleDateString()}
                            </div>
                        </div>
                    </div>

                    {/* Sidebar Actions */}
                    <div style={{ flex: 1 }}>
                        <button style={{ ...styles.actionBtn, ...styles.saveBtn }} onClick={handleSavePDF}>
                            SAVE AS PDF
                        </button>
                        <button
                            style={{ ...styles.actionBtn, ...styles.deleteBtn, opacity: selectedId ? 1 : 0.5 }}
                            onClick={handleDelete}
                            disabled={!selectedId}
                        >
                            DELETE
                        </button>
                    </div>

                    <Navigation onNavigate={onNavigate} activePage="logs" />
                </div>
            }
        >
            {/* Main Content Area: Table */}
            <div style={styles.tableContainer}>
                <table style={styles.table}>
                    <thead>
                        <tr>
                            <th style={styles.th}>Date</th>
                            <th style={styles.th}>Length</th>
                            <th style={styles.th}>Feed</th>
                            <th style={styles.th}>Weight</th>
                            <th style={styles.th}>Pop</th>
                            <th style={styles.th}>Temp</th>
                            <th style={styles.th}>pH</th>
                            <th style={styles.th}>Lvl</th>
                            <th style={styles.th}>Turb</th>
                        </tr>
                    </thead>
                    <tbody>
                        {logs.map((log) => (
                            <tr
                                key={log.id}
                                style={selectedId === log.id ? styles.selectedRow : {}}
                                onClick={() => setSelectedId(log.id)}
                            >
                                <td style={styles.td}>{log.date}</td>
                                <td style={styles.td}>{log.len}</td>
                                <td style={styles.td}>{log.feed}</td>
                                <td style={styles.td}>{log.w}</td>
                                <td style={styles.td}>{log.pop}</td>
                                <td style={styles.td}>{log.temp}</td>
                                <td style={styles.td}>{log.ph}</td>
                                <td style={styles.td}>{log.lvl}</td>
                                <td style={styles.td}>{log.turb}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </Layout>
    );
};

export default LogRecords;
