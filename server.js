import express from 'express';
import cors from 'cors';

const app = express();
app.use(cors());

// Mock Data State
let sensorData = {
    temperature: 25.0,
    ph: 7.0,
    turbidity: 5,     // 5 = Clear, 100 = Turbid (Mocking digital logic)
    water_level: 75,
    do: 6.5,
    bod: 2.0,
    tds: 350
};

// Helper to generate realistic random fluctuation
const fluctuate = (val, min, max, step = 0.1) => {
    const change = (Math.random() - 0.5) * step;
    let newVal = val + change;
    if (newVal < min) newVal = min;
    if (newVal > max) newVal = max;
    return parseFloat(newVal.toFixed(2));
};

// Update loop to simulate live data
setInterval(() => {
    sensorData.temperature = fluctuate(sensorData.temperature, 24, 30, 0.5);
    sensorData.ph = fluctuate(sensorData.ph, 6.0, 8.0, 0.1);
    sensorData.water_level = fluctuate(sensorData.water_level, 70, 80, 1.0);

    // Randomly flip turbidity occasionally
    if (Math.random() > 0.95) {
        sensorData.turbidity = sensorData.turbidity === 5 ? 100 : 5;
    }
}, 2000);

app.get('/api/sensors', (req, res) => {
    res.json(sensorData);
});

const PORT = 5000;
app.listen(PORT, () => {
    console.log(`Mock Sensor Server running on http://localhost:${PORT}`);
});
