import React from 'react';

const NotificationPanel = ({ sensorData }) => {
    const notifications = [];

    if (sensorData) {
        if (sensorData.ph > 8.5 || sensorData.ph < 6.5) { // Assuming < 6.5 is also abnormal, or just > 8.5
            // User specifically asked for "High pH Level", but let's cover abnormal
            if (sensorData.ph > 8.5) {
                notifications.push({
                    title: "High pH Level",
                    message: "pH LEVEL ABOVE SAFE THRESHOLD — AUTOMATED AERATION ACTIVATED. PLEASE CHECK WATER CHEMISTRY",
                    color: "#F04438"
                });
            } else {
                notifications.push({
                    title: "Low pH Level",
                    message: "pH LEVEL BELOW SAFE THRESHOLD. PLEASE CHECK WATER CHEMISTRY",
                    color: "#F04438"
                });
            }
        }
        
        if (sensorData.temp < 25 || sensorData.temp > 32) {
            notifications.push({
                title: "Temperature Out of Range",
                message: "WATER TEMPERATURE OUT OF OPTIMAL RANGE — AUTOMATED COOLING/HEATING RESPONSE INITIATED",
                color: "#F79009"
            });
        }
        
        if (sensorData.turbidity > 25) {
            notifications.push({
                title: "High Turbidity / Low Visibility",
                message: "HIGH TURBIDITY DETECTED — FEEDING TEMPORARILY SUSPENDED AND AUTOMATED WATER CIRCULATION ENABLED",
                color: "#F79009"
            });
        }
        
        if (sensorData.water_level < 50) {
            notifications.push({
                title: "Low Water Level",
                message: "WATER LEVEL BELOW MINIMUM THRESHOLD — AUTOMATED REFILLING SYSTEM ACTIVATED. PLEASE INSPECT FOR POSSIBLE LEAKS",
                color: "#F04438"
            });
        }
    }

    if (notifications.length === 0) {
        notifications.push({
            title: "Normal Condition",
            message: "ALL WATER QUALITY PARAMETERS ARE WITHIN NORMAL RANGE",
            color: "#12B76A" // Green
        });
    }

    const styles = {
        container: {
            marginBottom: '4px',
            flex: 1, // Let it grow if needed
            overflowY: 'auto', // Scroll if too many notifications
            maxHeight: '120px' // Cap height so it doesn't break layout
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
            padding: '8px',
            textAlign: 'center',
            border: '1px solid #475467',
            marginBottom: '4px',
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
            color: '#fff',
            fontWeight: 'bold'
        },
        message: {
            fontSize: '0.65rem',
            fontWeight: 'bold',
        }
    };

    return (
        <div style={styles.container}>
            <span style={styles.header}>Notifications</span>
            {notifications.map((notif, index) => (
                <div key={index} style={{...styles.box, borderLeft: `4px solid ${notif.color}`}}>
                    <div style={styles.title}>{notif.title}</div>
                    <div style={{...styles.message, color: notif.color}}>{notif.message}</div>
                </div>
            ))}
        </div>
    );
};

export default NotificationPanel;
