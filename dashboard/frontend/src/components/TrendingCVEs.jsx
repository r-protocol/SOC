import React, { useState, useEffect } from 'react';
import api from '../utils/api';

function TrendingCVEs({ timeRange }) {
  const [cves, setCves] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Build time range parameters
    let timeParams = '';
    if (timeRange.type === 'daterange' && timeRange.startDate && timeRange.endDate) {
      timeParams = `?start_date=${timeRange.startDate}&end_date=${timeRange.endDate}`;
    } else if (timeRange.days) {
      timeParams = `?days=${timeRange.days}`;
    }
    
    api.getTrendingCVEs({})
      .then(data => {
        setCves(data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, [timeRange]);

  if (loading) return <div className="card loading">Loading CVEs...</div>;

  const getSeverityColor = (severity) => {
    const colors = {
      'CRITICAL': '#ea4335',
      'HIGH': '#ff6d01',
      'MEDIUM': '#fbbc04',
      'LOW': '#34a853',
      'UNKNOWN': '#a1a1aa'
    };
    return colors[severity] || colors.UNKNOWN;
  };

  return (
    <div className="card">
      <div className="card-title">🔥 Trending CVEs / Vulnerabilities</div>
      {cves.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '40px', color: '#a1a1aa' }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>🛡️</div>
          <div>No CVEs detected in articles</div>
          <div style={{ fontSize: '12px', marginTop: '8px' }}>
            CVEs are extracted from analyzed articles with IOCs
          </div>
        </div>
      ) : (
        <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
          {cves.map((cve, idx) => (
            <div 
              key={idx}
              style={{
                padding: '14px',
                margin: '10px 0',
                background: '#1e1e2e',
                borderRadius: '8px',
                borderLeft: `4px solid ${getSeverityColor(cve.severity)}`,
                transition: 'all 0.2s',
                cursor: 'pointer'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = '#2a2a3e';
                e.currentTarget.style.transform = 'translateX(4px)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = '#1e1e2e';
                e.currentTarget.style.transform = 'translateX(0)';
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '8px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flex: 1 }}>
                  <span style={{ 
                    fontWeight: '700', 
                    fontSize: '15px',
                    color: '#4285f4',
                    fontFamily: 'monospace'
                  }}>
                    {cve.cve}
                  </span>
                  <span style={{
                    padding: '3px 10px',
                    borderRadius: '4px',
                    fontSize: '11px',
                    fontWeight: '700',
                    background: `${getSeverityColor(cve.severity)}20`,
                    color: getSeverityColor(cve.severity)
                  }}>
                    {cve.severity}
                  </span>
                  {cve.count > 1 && (
                    <span style={{
                      padding: '3px 8px',
                      borderRadius: '4px',
                      fontSize: '10px',
                      fontWeight: '600',
                      background: '#4285f420',
                      color: '#4285f4'
                    }}>
                      {cve.count}x mentioned
                    </span>
                  )}
                </div>
                <div style={{ 
                  fontSize: '11px', 
                  color: '#a1a1aa',
                  whiteSpace: 'nowrap',
                  marginLeft: '10px'
                }}>
                  {cve.date ? new Date(cve.date).toLocaleDateString() : ''}
                </div>
              </div>
              
              {cve.context && (
                <div style={{ 
                  fontSize: '12px', 
                  color: '#a1a1aa',
                  marginBottom: '6px',
                  fontStyle: 'italic'
                }}>
                  {cve.context}
                </div>
              )}
              
              {cve.latest_article && (
                <div style={{ 
                  fontSize: '12px', 
                  color: '#e0e0e0',
                  lineHeight: '1.4',
                  marginTop: '6px'
                }}>
                  📰 {cve.latest_article.substring(0, 80)}{cve.latest_article.length > 80 ? '...' : ''}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default TrendingCVEs;
