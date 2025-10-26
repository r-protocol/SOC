import React, { useState, useEffect } from 'react';
import PipelineOverview from './components/PipelineOverview';
import ThreatTimeline from './components/ThreatTimeline';
import CategoryDistribution from './components/CategoryDistribution';
import RecentThreats from './components/RecentThreats';
import IOCStats from './components/IOCStats';
import RSSFeedStats from './components/RSSFeedStats';
import ThreatFamilies from './components/ThreatFamilies';

function App() {
  const [refreshInterval, setRefreshInterval] = useState(60000); // 60 seconds
  const [error, setError] = useState(null);

  // Auto-refresh
  useEffect(() => {
    const interval = setInterval(() => {
      window.location.reload();
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [refreshInterval]);

  // Error boundary
  useEffect(() => {
    const handleError = (event) => {
      console.error('Global error:', event.error);
      setError(event.error.message);
    };
    window.addEventListener('error', handleError);
    return () => window.removeEventListener('error', handleError);
  }, []);

  if (error) {
    return (
      <div style={{padding: '40px', color: '#ea4335', background: '#1e1e2e', minHeight: '100vh'}}>
        <h1>Error Loading Dashboard</h1>
        <p>{error}</p>
        <button onClick={() => window.location.reload()} style={{padding: '10px 20px', marginTop: '20px'}}>
          Reload
        </button>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <header className="header">
        <h1>🛡️ SOC Threat Intelligence Dashboard</h1>
        <p className="header-subtitle">
          Real-time threat monitoring and analysis • Auto-refresh every 60s
        </p>
      </header>

      <div className="grid grid-4">
        <PipelineOverview />
      </div>

      <div className="grid grid-2" style={{ marginTop: '24px' }}>
        <ThreatTimeline />
        <CategoryDistribution />
      </div>

      <div className="grid grid-2" style={{ marginTop: '24px' }}>
        <ThreatFamilies />
        <IOCStats />
      </div>

      <div style={{ marginTop: '24px' }}>
        <RecentThreats />
      </div>

      <div style={{ marginTop: '24px' }}>
        <RSSFeedStats />
      </div>
    </div>
  );
}

export default App;
