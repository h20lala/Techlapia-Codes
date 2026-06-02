import React from 'react';

const NotificationPanel = ({ sensorData }) => {
    let finalNotification = null;
    const anomalies = [];

    if (sensorData) {
        if (sensorData.ph > 8.5) {
            anomalies.push({
                shortTitle: "High pH",
                title: "High pH Level",
                message: "pH LEVEL ABOVE SAFE THRESHOLD — AUTOMATED AERATION ACTIVATED. PLEASE CHECK WATER CHEMISTRY",
                color: "#F04438"
            });
        } else if (sensorData.ph < 6.5) {
            anomalies.push({
                shortTitle: "Low pH",
                title: "Low pH Level",
                message: "pH LEVEL BELOW SAFE THRESHOLD. PLEASE CHECK WATER CHEMISTRY",
                color: "#F04438"
            });
        }
        
        if (sensorData.temp < 25 || sensorData.temp > 32) {
            anomalies.push({
                shortTitle: sensorData.temp < 25 ? "Low Temp" : "High Temp",
                title: "Temperature Out of Range",
                message: "WATER TEMPERATURE OUT OF OPTIMAL RANGE — AUTOMATED COOLING/HEATING RESPONSE INITIATED",
                color: "#F79009"
            });
        }
        
        if (sensorData.turbidity > 25) {
            anomalies.push({
                shortTitle: "High Turbidity",
                title: "High Turbidity / Low Visibility",
                message: "HIGH TURBIDITY DETECTED — FEEDING TEMPORARILY SUSPENDED AND AUTOMATED WATER CIRCULATION ENABLED",
                color: "#F79009"
            });
        }
        
        if (sensorData.water_level < 50) {
            anomalies.push({
                shortTitle: "Low Water Level",
                title: "Low Water Level",
                message: "WATER LEVEL BELOW MINIMUM THRESHOLD — AUTOMATED REFILLING SYSTEM ACTIVATED. PLEASE INSPECT FOR POSSIBLE LEAKS",
                color: "#F04438"
            });
        }
    }

    if (anomalies.length === 0) {
        finalNotification = {
            title: "Normal Condition",
            message: "ALL WATER QUALITY PARAMETERS ARE WITHIN NORMAL RANGE",
            color: "#12B76A" // Green
        };
    } else if (anomalies.length === 1) {
        finalNotification = anomalies[0];
    } else {
        // Multiple anomalies
        const shortTitles = anomalies.map(a => a.shortTitle).join(" AND ");
        const combinedMessage = anomalies.map(a => a.message).join(" | ");
        
        finalNotification = {
            title: `MULTIPLE ANOMALIES: ${shortTitles.toUpperCase()}`,
            message: combinedMessage,
            color: "#F04438" // Red for critical multi-failure
        };
    }

    const styles = {
        container: {
            marginBottom: '4px',
            overflowY: 'auto'
        },
        header: {
            fontSize: '0.75rem',
            color: '#98A2B3',
            marginBottom: '4px',
            display: 'block',
        }
    };

    return (
        <div style={styles.container}>
            <span style={styles.header}>Notifications</span>
            <div style={{
                background: '#1D2939',
                borderRadius: '8px',
                padding: '8px',
                textAlign: 'center',
                border: '1px solid #475467',
                borderLeft: `4px solid ${finalNotification.color}`,
                marginBottom: '4px',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                alignItems: 'center'
            }}>
                <div style={{
                    fontSize: '0.65rem',
                    textTransform: 'uppercase',
                    letterSpacing: '0.5px',
                    marginBottom: '2px',
                    color: '#fff',
                    fontWeight: 'bold'
                }}>{finalNotification.title}</div>
                <div style={{
                    fontSize: '0.65rem',
                    fontWeight: 'bold',
                    color: finalNotification.color
                }}>{finalNotification.message}</div>
            </div>
        </div>
    );
};

export default NotificationPanel;
