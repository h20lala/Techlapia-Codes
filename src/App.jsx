import React, { useState } from 'react';
import Dashboard from './pages/Dashboard.jsx';
import Settings from './pages/Settings.jsx';
import LogRecords from './pages/LogRecords.jsx';

import GlobalDragScroll from './components/GlobalDragScroll.jsx';

function App() {
    const [currentPage, setCurrentPage] = useState('dashboard');

    const navigate = (page) => {
        setCurrentPage(page);
    };

    const renderPage = () => {
        switch (currentPage) {
            case 'dashboard':
                return <Dashboard onNavigate={navigate} />;
            case 'settings':
                return <Settings onNavigate={navigate} />;
            case 'logs':
                return <LogRecords onNavigate={navigate} />;
            default:
                return <Dashboard onNavigate={navigate} />;
        }
    };

    return (
        <div className="app-container">
            <GlobalDragScroll />
            {renderPage()}
        </div>
    );
}

export default App;
