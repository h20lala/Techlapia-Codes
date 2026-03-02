import React, { useState, useEffect } from 'react';
import Layout from '../components/Layout.jsx';
import Navigation from '../components/Navigation.jsx';
import StatusCard from '../components/StatusCard.jsx';
import CameraFeed from '../components/CameraFeed.jsx';

const Settings = ({ onNavigate }) => {
    const [currentTime, setCurrentTime] = useState(new Date());

    // Real-time Clock
    useEffect(() => {
        const timer = setInterval(() => setCurrentTime(new Date()), 1000);
        return () => clearInterval(timer);
    }, []);

    const [inputs, setInputs] = useState({
        population: 15,
        length: 172,
        width: 194,
        depth: 75,
        weight: 250,
        mock_weight: 20
    });
    const [density, setDensity] = useState(0);
    const [initialLoaded, setInitialLoaded] = useState(false);

    // Fetch settings on mount
    useEffect(() => {
        const fetchSettings = async () => {
            try {
                const res = await fetch(`http://${window.location.hostname}:5000/api/settings`);
                if (res.ok) {
                    const data = await res.json();
                    setInputs(data);
                }
            } catch (err) {
                console.error("Error fetching settings:", err);
            } finally {
                setInitialLoaded(true);
            }
        };
        fetchSettings();
    }, []);

    // Auto-save settings when inputs change
    useEffect(() => {
        if (!initialLoaded) return;
        const timer = setTimeout(async () => {
            try {
                await fetch(`http://${window.location.hostname}:5000/api/settings`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(inputs)
                });
            } catch (err) {
                console.error("Error saving settings:", err);
            }
        }, 1000);
        return () => clearTimeout(timer);
    }, [inputs, initialLoaded]);

    useEffect(() => {
        const volumeM3 = (inputs.length * inputs.width * inputs.depth) / 1000000;
        const weightKg = inputs.weight / 1000;
        let calculatedDensity = 0;

        if (volumeM3 > 0) {
            calculatedDensity = (inputs.population * weightKg) / volumeM3;
        }

        setDensity(calculatedDensity.toFixed(2));
    }, [inputs]);

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setInputs(prev => ({
            ...prev,
            [name]: parseFloat(value) || 0
        }));
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

        inputGroup: {
            background: 'var(--color-secondary)', padding: '10px',
            borderRadius: '8px', marginBottom: '4px'
        },
        label: {
            fontSize: '0.75rem', color: 'var(--color-text-muted)', display: 'block', marginBottom: '4px'
        },
        input: {
            width: '100%', background: 'rgba(0,0,0,0.2)', border: '1px solid var(--glass-border)',
            padding: '6px', borderRadius: '4px', color: '#fff', fontSize: '1rem', textAlign: 'center'
        },
        row: { display: 'flex', gap: '6px', alignItems: 'center' }
    };

    return (
        <Layout
            sidebar={
                <div style={styles.sidebarContainer}>
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

                    {/* Initial Population Input */}
                    <div style={styles.inputGroup}>
                        <span style={styles.label}>Initial Population (Tn)</span>
                        <input
                            style={styles.input}
                            name="population"
                            value={inputs.population}
                            onChange={handleInputChange}
                        />
                    </div>

                    {/* Tank Dimensions Input */}
                    <div style={styles.inputGroup}>
                        <span style={styles.label}>Tank Dimensions (cm)</span>
                        <div style={styles.row}>
                            <div>
                                <span style={{ fontSize: '0.65rem', color: '#98A2B3' }}>Length</span>
                                <input style={styles.input} name="length" value={inputs.length} onChange={handleInputChange} />
                            </div>
                            <div>
                                <span style={{ fontSize: '0.65rem', color: '#98A2B3' }}>Width</span>
                                <input style={styles.input} name="width" value={inputs.width} onChange={handleInputChange} />
                            </div>
                            <div>
                                <span style={{ fontSize: '0.65rem', color: '#98A2B3' }}>Depth</span>
                                <input style={styles.input} name="depth" value={inputs.depth} onChange={handleInputChange} />
                            </div>
                        </div>
                    </div>

                    {/* Target Weight Input */}
                    <div style={styles.inputGroup}>
                        <span style={styles.label}>Target Fish Weight (Tw) in grams</span>
                        <input
                            style={styles.input}
                            name="weight"
                            value={inputs.weight}
                            onChange={handleInputChange}
                        />
                    </div>

                    {/* Current Fish Weight Input (Mock) */}
                    <div style={styles.inputGroup}>
                        <span style={styles.label}>Current Fish Weight (Mock) in grams</span>
                        <input
                            style={styles.input}
                            name="mock_weight"
                            value={inputs.mock_weight}
                            onChange={handleInputChange}
                        />
                    </div>

                    {/* Calculated Density */}
                    <StatusCard
                        label={`Stocking Density (Td) = (Tn × Tw) / V`}
                        value={`${density} kg/m³`}
                        status="Normal"
                    />

                    <Navigation onNavigate={onNavigate} activePage="settings" />
                </div>
            }
        >
            <div style={{ width: '100%', height: '100%', background: '#000', position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'center', overflow: 'hidden' }}>
                <CameraFeed />
            </div>
        </Layout>
    );
};

export default Settings;
