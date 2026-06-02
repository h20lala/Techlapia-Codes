import React from 'react';

const ActionButtons = ({ onFeederTriggered }) => {
    const [showFeederInput, setShowFeederInput] = React.useState(false);
    const [feederWeight, setFeederWeight] = React.useState('');

    const handleFeeder = async () => {
        if (!showFeederInput) {
            setShowFeederInput(true);
            return;
        }

        const weightVal = parseFloat(feederWeight);
        if (isNaN(weightVal) || weightVal <= 0) {
            alert("Please enter a valid weight in grams.");
            return;
        }

        try {
            const res = await fetch(`http://${window.location.hostname}:5000/api/feed`, { 
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ weight: weightVal })
            });
            if (res.ok && onFeederTriggered) {
                onFeederTriggered();
            }
            setShowFeederInput(false);
            setFeederWeight('');
        } catch (error) {
            console.error("Failed to trigger feeder", error);
        }
    };
    const [isWaterFilterOn, setIsWaterFilterOn] = React.useState(false);

    const toggleWaterFilter = async () => {
        const newState = !isWaterFilterOn;
        setIsWaterFilterOn(newState);
        try {
            await fetch(`http://${window.location.hostname}:5000/api/water-filter`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ state: newState ? "on" : "off" })
            });
        } catch (error) {
            console.error("Failed to toggle water filter", error);
            // Revert on failure
            setIsWaterFilterOn(!newState);
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
        waterBtn: { 
            background: isWaterFilterOn ? '#1570EF' : '#98A2B3',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: '8px 12px'
        },
        feederBtn: { background: '#F79009' }, // Orange
        input: {
            width: '100%',
            padding: '8px',
            borderRadius: '6px',
            border: '1px solid #ccc',
            fontSize: '0.75rem',
            marginBottom: '4px',
            boxSizing: 'border-box'
        },
        switchKnob: {
            width: '16px',
            height: '16px',
            borderRadius: '50%',
            background: '#fff',
            transition: 'transform 0.2s',
            transform: isWaterFilterOn ? 'translateX(14px)' : 'translateX(0)',
        },
        switchTrack: {
            width: '34px',
            height: '20px',
            borderRadius: '10px',
            background: isWaterFilterOn ? 'rgba(255,255,255,0.4)' : 'rgba(0,0,0,0.2)',
            display: 'flex',
            alignItems: 'center',
            padding: '2px',
            boxSizing: 'border-box'
        }
    };

    return (
        <div style={styles.container}>
            <span style={styles.header}>Override</span>
            <div style={styles.rowStyles}>
                <button style={{ ...styles.button, ...styles.waterBtn }} onClick={toggleWaterFilter}>
                    <span>WATER FILTER</span>
                    <div style={styles.switchTrack}>
                        <div style={styles.switchKnob} />
                    </div>
                </button>
                
                {!showFeederInput ? (
                    <button style={{ ...styles.button, ...styles.feederBtn }} onClick={handleFeeder}>FEEDER</button>
                ) : (
                    <div>
                        <input 
                            type="number" 
                            style={styles.input} 
                            placeholder="Enter weight (g)" 
                            value={feederWeight} 
                            onChange={(e) => setFeederWeight(e.target.value)} 
                        />
                        <button style={{ ...styles.button, ...styles.feederBtn }} onClick={handleFeeder}>SUBMIT FEEDER</button>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ActionButtons;
