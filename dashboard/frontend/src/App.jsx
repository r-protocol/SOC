import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import PipelineOverview from './components/PipelineOverview';
import ThreatTimeline from './components/ThreatTimeline';
import CategoryDistribution from './components/CategoryDistribution';
import RecentThreats from './components/RecentThreats';
import IOCStats from './components/IOCStats';
import RSSFeedStats from './components/RSSFeedStats';
import TopTargetedIndustries from './components/TopTargetedIndustries';
import ThreatActorGeoMap from './components/ThreatActorGeoMap';
import AttackVectorDistribution from './components/AttackVectorDistribution';
import TrendingCVEs from './components/TrendingCVEs';
import ArticlePage from './components/ArticlePage';

function Dashboard() {
  const [refreshInterval, setRefreshInterval] = useState(300000); // 5 minutes (300 seconds)
  const [error, setError] = useState(null);
  const [timeRange, setTimeRange] = useState({ type: '7days', days: 7 });
  const [showCustomDays, setShowCustomDays] = useState(false);
  const [showDateRange, setShowDateRange] = useState(false);
  const [customDays, setCustomDays] = useState(7);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

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

  const handleTimeRangeChange = (type) => {
    setShowCustomDays(false);
    setShowDateRange(false);

    switch (type) {
      case '1day':
        setTimeRange({ type, days: 1 });
        break;
      case '3days':
        setTimeRange({ type, days: 3 });
        break;
      case '7days':
        setTimeRange({ type, days: 7 });
        break;
      case '15days':
        setTimeRange({ type, days: 15 });
        break;
      case '30days':
        setTimeRange({ type, days: 30 });
        break;
      case 'custom':
        setShowCustomDays(true);
        setTimeRange({ type, days: customDays });
        break;
      case 'daterange':
        setShowDateRange(true);
        setTimeRange({ type, startDate, endDate });
        break;
      default:
        setTimeRange({ type: '7days', days: 7 });
    }
  };

  const handleCustomDaysApply = () => {
    if (customDays > 0) {
      setTimeRange({ type: 'custom', days: parseInt(customDays) });
    }
  };

  const handleDateRangeApply = () => {
    if (startDate && endDate) {
      setTimeRange({ type: 'daterange', startDate, endDate });
    }
  };

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
          Real-time threat monitoring and analysis • Auto-refresh every 5 minutes
        </p>
        
        {/* Time Range Filter */}
        <div style={{ 
          marginTop: '20px', 
          padding: '16px', 
          background: '#2a2a3a', 
          borderRadius: '12px',
          border: '1px solid #3a3a4a'
        }}>
          <div style={{ marginBottom: '12px', color: '#a1a1aa', fontSize: '14px', fontWeight: '600' }}>
            📅 Time Range Filter
          </div>
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', alignItems: 'center' }}>
            {['1day', '3days', '7days', '15days', '30days', 'custom', 'daterange'].map(range => (
              <button
                key={range}
                onClick={() => handleTimeRangeChange(range)}
                style={{
                  padding: '8px 16px',
                  borderRadius: '6px',
                  border: timeRange.type === range ? '2px solid #4285f4' : '2px solid #3a3a4a',
                  background: timeRange.type === range ? '#4285f420' : '#1e1e2e',
                  color: timeRange.type === range ? '#4285f4' : '#a1a1aa',
                  cursor: 'pointer',
                  fontSize: '13px',
                  fontWeight: timeRange.type === range ? '600' : '400',
                  transition: 'all 0.2s ease'
                }}
              >
                {range === '1day' ? '1 Day' :
                 range === '3days' ? '3 Days' :
                 range === '7days' ? '7 Days' :
                 range === '15days' ? '15 Days' :
                 range === '30days' ? '30 Days' :
                 range === 'custom' ? 'Custom Days' :
                 'Date Range'}
              </button>
            ))}
            
            {showCustomDays && (
              <div style={{ display: 'flex', gap: '8px', alignItems: 'center', marginLeft: '8px' }}>
                <input
                  type="number"
                  min="1"
                  value={customDays}
                  onChange={(e) => setCustomDays(e.target.value)}
                  placeholder="Days"
                  style={{
                    padding: '8px 12px',
                    borderRadius: '6px',
                    border: '2px solid #3a3a4a',
                    background: '#1e1e2e',
                    color: '#e0e0e0',
                    width: '100px',
                    fontSize: '13px'
                  }}
                />
                <button
                  onClick={handleCustomDaysApply}
                  style={{
                    padding: '8px 16px',
                    borderRadius: '6px',
                    border: '2px solid #34a853',
                    background: '#34a85320',
                    color: '#34a853',
                    cursor: 'pointer',
                    fontSize: '13px',
                    fontWeight: '600'
                  }}
                >
                  Apply
                </button>
              </div>
            )}
            
            {showDateRange && (
              <div style={{ display: 'flex', gap: '8px', alignItems: 'center', marginLeft: '8px', flexWrap: 'wrap' }}>
                <input
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  style={{
                    padding: '8px 12px',
                    borderRadius: '6px',
                    border: '2px solid #3a3a4a',
                    background: '#1e1e2e',
                    color: '#e0e0e0',
                    fontSize: '13px'
                  }}
                />
                <span style={{ color: '#a1a1aa' }}>to</span>
                <input
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  style={{
                    padding: '8px 12px',
                    borderRadius: '6px',
                    border: '2px solid #3a3a4a',
                    background: '#1e1e2e',
                    color: '#e0e0e0',
                    fontSize: '13px'
                  }}
                />
                <button
                  onClick={handleDateRangeApply}
                  style={{
                    padding: '8px 16px',
                    borderRadius: '6px',
                    border: '2px solid #34a853',
                    background: '#34a85320',
                    color: '#34a853',
                    cursor: 'pointer',
                    fontSize: '13px',
                    fontWeight: '600'
                  }}
                >
                  Apply
                </button>
              </div>
            )}
          </div>
          
          {timeRange.type && (
            <div style={{ marginTop: '12px', fontSize: '12px', color: '#4285f4' }}>
              {timeRange.type === 'daterange' && timeRange.startDate && timeRange.endDate ? 
                `📊 Showing data from ${new Date(timeRange.startDate).toLocaleDateString()} to ${new Date(timeRange.endDate).toLocaleDateString()}` :
                timeRange.days ? `📊 Showing data from last ${timeRange.days} day${timeRange.days > 1 ? 's' : ''}` : ''
              }
            </div>
          )}
        </div>
      </header>

      <div className="grid grid-4">
        <PipelineOverview timeRange={timeRange} />
      </div>

      <div className="grid grid-2" style={{ marginTop: '24px' }}>
        <ThreatTimeline timeRange={timeRange} />
        <CategoryDistribution timeRange={timeRange} />
      </div>

      <div className="grid grid-2" style={{ marginTop: '24px' }}>
        <TopTargetedIndustries timeRange={timeRange} />
        <IOCStats timeRange={timeRange} />
      </div>

      <div style={{ marginTop: '24px' }}>
        <ThreatActorGeoMap timeRange={timeRange} />
      </div>

      <div className="grid grid-2" style={{ marginTop: '24px' }}>
        <AttackVectorDistribution timeRange={timeRange} />
        <TrendingCVEs timeRange={timeRange} />
      </div>

      <div style={{ marginTop: '24px' }}>
        <RecentThreats timeRange={timeRange} />
      </div>

      <div style={{ marginTop: '24px' }}>
        <RSSFeedStats timeRange={timeRange} />
      </div>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/article" element={<ArticlePage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
