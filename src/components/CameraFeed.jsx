import React, { useRef, useEffect, useState } from 'react';

const CameraFeed = () => {
    const streamUrl = `http://${window.location.hostname}:5000/video_feed`;
    const [error, setError] = useState(false);

    return (
        <div style={{ width: '100%', height: '100%', position: 'relative', background: '#000', overflow: 'hidden' }}>

            {/* Server Stream (RPi) */}
            <img
                src={streamUrl}
                alt="Connecting to RPi Camera..."
                style={{ width: '100%', height: '100%', objectFit: 'contain' }}
                onError={() => setError(true)}
            />

            {/* Error / Fallback State */}
            {error && (
                <div style={{
                    position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)',
                    color: '#fff', textAlign: 'center'
                }}>
                    <p>No Signal from Server</p>
                </div>
            )}

            {/* Label Overlay */}
            <div style={{
                position: 'absolute', top: '10px', left: '10px',
                background: 'rgba(255,0,0,0.8)', color: '#fff', padding: '2px 8px',
                borderRadius: '4px', fontSize: '0.7rem', fontWeight: 'bold'
            }}>
                LIVE
            </div>
        </div>
    );
};

export default CameraFeed;
