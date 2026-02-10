import React, { useRef, useEffect, useState } from 'react';

const CameraFeed = () => {
    const videoRef = useRef(null);
    const [useLocal, setUseLocal] = useState(false);
    const [streamUrl, setStreamUrl] = useState(`http://${window.location.hostname}:5000/video_feed`);
    const [error, setError] = useState(false);

    // Function to start local webcam (Laptop Test)
    const startLocalCamera = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            if (videoRef.current) {
                videoRef.current.srcObject = stream;
            }
            setError(false);
        } catch (err) {
            console.error("Error accessing webcam:", err);
            setError(true);
        }
    };

    // Toggle between modes
    const toggleMode = () => {
        if (!useLocal) {
            setUseLocal(true);
            startLocalCamera();
        } else {
            setUseLocal(false);
            // Stop tracks
            if (videoRef.current && videoRef.current.srcObject) {
                videoRef.current.srcObject.getTracks().forEach(track => track.stop());
                videoRef.current.srcObject = null;
            }
        }
    };

    return (
        <div style={{ width: '100%', height: '100%', position: 'relative', background: '#000', overflow: 'hidden' }}>

            {/* Display Logic */}
            {useLocal ? (
                /* Local Webcam (Laptop Test) */
                <video
                    ref={videoRef}
                    autoPlay
                    playsInline
                    muted
                    style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                />
            ) : (
                /* Server Stream (RPi) */
                <img
                    src={streamUrl}
                    alt="Connecting to RPi Camera..."
                    style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                    onError={() => setError(true)}
                />
            )}

            {/* Error / Fallback State */}
            {error && !useLocal && (
                <div style={{
                    position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)',
                    color: '#fff', textAlign: 'center'
                }}>
                    <p>No Signal from Server</p>
                    <button
                        onClick={toggleMode}
                        style={{
                            padding: '8px 16px', background: '#1570EF', border: 'none',
                            color: '#fff', borderRadius: '4px', cursor: 'pointer', marginTop: '8px'
                        }}
                    >
                        Test Laptop Camera
                    </button>
                </div>
            )}

            {/* Manual Toggle Button (Visible on hover or always transparent) */}
            <button
                onClick={toggleMode}
                style={{
                    position: 'absolute', bottom: '10px', right: '10px',
                    padding: '4px 8px', background: 'rgba(0,0,0,0.5)',
                    color: '#fff', border: '1px solid #fff', borderRadius: '4px',
                    cursor: 'pointer', fontSize: '0.7rem', zIndex: 10
                }}
            >
                {useLocal ? "Switch to Server Stream" : "Switch to Laptop Cam"}
            </button>

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
