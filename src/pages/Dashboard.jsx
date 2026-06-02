import React, { useState, useEffect } from 'react';
import Layout from '../components/Layout.jsx';
import NotificationPanel from '../components/NotificationPanel.jsx';
import FeedingSchedule from '../components/FeedingSchedule.jsx';
import ActionButtons from '../components/ActionButtons.jsx';
import Navigation from '../components/Navigation.jsx';
import CameraFeed from '../components/CameraFeed.jsx';

// Sensor Strip Component 
const SensorStrip = ({ label, value, status }) => {
    let statusColor = '#66C2FF'; // Default Blue
    if (status === 'High' || status === 'Low') statusColor = '#F04438'; // Red
    else if (status === 'Warning') statusColor = '#F79009'; // Orange

    return (
        <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            fontSize: '0.7rem',
            padding: '4px 0',
            borderBottom: '1px solid rgba(255,255,255,0.1)'
        }}>
            <span style={{ color: '#fff' }}>{label}: <span style={{ fontWeight: 'bold' }}>{value}</span></span>
            <span style={{ color: statusColor }}>| {status}</span>
        </div>
    );
};

const Dashboard = ({ onNavigate }) => {
    const [currentTime, setCurrentTime] = useState(new Date());
    const [sensorData, setSensorData] = useState({
        temp: "-",
        ph: "-",
        turbidity: "-",
        water_level: "-",
        water_filter_on: false
    });
    const [refreshTrigger, setRefreshTrigger] = useState(0);

    // Real-time Clock
    useEffect(() => {
        const timer = setInterval(() => setCurrentTime(new Date()), 1000);
        return () => clearInterval(timer);
    }, []);

    // Fetch Sensor Data
    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await fetch(`http://${window.location.hostname}:5000/api/sensors`);
                const data = await response.json();
                if (data) {
                    setSensorData({
                        temp: data.temperature,
                        ph: data.ph,
                        turbidity: data.turbidity,
                        water_level: data.water_level,
                        water_filter_on: data.water_filter_on
                    });
                }
            } catch (error) {
                console.error("Error fetching sensor data:", error);
            }
        };

        const sensorTimer = setInterval(fetchData, 2000); // Poll every 2 seconds
        fetchData(); // Initial call
        return () => clearInterval(sensorTimer);
    }, []);

    // Determine Status based on Table 1 ref
    const getStatus = (val, type) => {
        if (val === "-") return "-";
        if (type === 'temp') {
            if (val < 25) return 'Low';
            if (val > 32) return 'High';
            return 'Normal';
        }
        if (type === 'ph') {
            if (val < 6.5) return 'Low';
            if (val > 8.5) return 'High';
            return 'Normal';
        }
        if (type === 'turb') {
            if (val > 25) return 'High'; // Turbidity
            return 'Normal';
        }
        if (type === 'level') {
            if (val < 50) return 'Low'; // Example threshold
            return 'Normal';
        }
        return 'Normal';
    };

    const styles = {
        cameraOverlay: {
            position: 'absolute', top: 0, left: 0, width: '100%', height: '100%',
            objectFit: 'cover', opacity: 0.1,
        },
        cameraText: {
            position: 'relative', zIndex: 2, fontWeight: '600', color: '#000',
            background: 'rgba(255,255,255,0.8)', padding: '8px 16px', borderRadius: '20px',
        },
        sidebarContainer: {
            display: 'flex', flexDirection: 'column', gap: '6px', minHeight: '100%',
            color: '#fff', fontFamily: 'var(--font-family-main)'
        },
        headerRow: {
            display: 'flex', justifyContent: 'space-between', alignItems: 'center',
            padding: '0 4px', marginBottom: '4px'
        },
        logoText: {
            fontSize: '1.4rem', fontWeight: 'bold', fontFamily: 'var(--font-family-display)', letterSpacing: '1px'
        },
        dateText: { fontSize: '0.7rem', color: '#98A2B3' },
        infoBox: {
            background: '#1D2939', borderRadius: '8px', padding: '8px',
            display: 'grid', gridTemplateColumns: '80px 1fr', gap: '12px', alignItems: 'center'
        },
        countBox: {
            display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center'
        },
        countLabel: { fontSize: '0.65rem', color: '#98A2B3', marginBottom: '2px' },
        countValue: { fontSize: '2.5rem', fontWeight: 'bold', lineHeight: '1' }
    };

    return (
        <Layout
            sidebar={
                <div style={styles.sidebarContainer}>
                    {/* Header Row: Live Time */}
                    <div style={styles.headerRow}>
                        <div style={styles.logoText}>TECHLAPIA</div>
                        <div style={{ textAlign: 'right' }}>
                            <div style={{ fontSize: '0.7rem', fontWeight: 'bold' }}>
                                {currentTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            </div>
                            <div style={styles.dateText}>
                                {currentTime.toLocaleDateString()}
                            </div>
                        </div>
                    </div>

                    <div style={styles.infoBox}>
                        <div style={styles.countBox}>
                            <span style={styles.countLabel}>Tilapia Count</span>
                            <span style={styles.countValue}>15</span>
                        </div>

                        <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
                            <SensorStrip
                                label="Temperature"
                                value={sensorData.temp === "-" ? "-" : `${Number(sensorData.temp).toFixed(1)}° C`}
                                status={getStatus(sensorData.temp, 'temp')}
                            />
                            <SensorStrip
                                label="Turbidity"
                                value={sensorData.turbidity === "-" ? "-" : `${sensorData.turbidity} NTU`}
                                status={getStatus(sensorData.turbidity, 'turb')}
                            />
                            <SensorStrip
                                label="pH Level"
                                value={sensorData.ph === "-" ? "-" : Number(sensorData.ph).toFixed(1)}
                                status={getStatus(sensorData.ph, 'ph')}
                            />
                            <SensorStrip
                                label="Water Level"
                                value={sensorData.water_level === "-" ? "-" : `${sensorData.water_level} cm`}
                                status={getStatus(sensorData.water_level, 'level')}
                            />
                        </div>
                    </div>

                    <NotificationPanel sensorData={sensorData} />
                    <FeedingSchedule refreshTrigger={refreshTrigger} />
                    <ActionButtons 
                        onFeederTriggered={() => setRefreshTrigger(prev => prev + 1)}
                        initialWaterFilterState={sensorData.water_filter_on}
                    />

                    <Navigation onNavigate={onNavigate} activePage="dashboard" />
                </div>
            }
        >
            <div style={{ width: '100%', height: '100%', background: '#000', position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'center', overflow: 'hidden' }}>
                {/* Live Camera Feed Component */}
                <CameraFeed />
            </div>
        </Layout>
    );
};

export default Dashboard;
