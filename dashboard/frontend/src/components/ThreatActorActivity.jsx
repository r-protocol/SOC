import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = 'http://localhost:5000/api';

function ThreatActorActivity({ timeRange }) {
  const [actors, setActors] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Build time range parameters
    let timeParams = '';
    if (timeRange.type === 'daterange' && timeRange.startDate && timeRange.endDate) {
      timeParams = `?start_date=${timeRange.startDate}&end_date=${timeRange.endDate}`;
    } else if (timeRange.days) {
      timeParams = `?days=${timeRange.days}`;
    }
    
    axios.get(`${API_BASE}/threat-actor-activity${timeParams}`)
      .then(res => {
        setActors(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, [timeRange]);

  if (loading) return <div className="card loading">Loading threat actors...</div>;

  const getCountryFlag = (country) => {
    const flags = {
      'Russia': '🇷🇺',
      'China': '🇨🇳',
      'North Korea': '🇰🇵',
      'Iran': '🇮🇷',
      'Unknown': '🏴‍☠️'
    };
    return flags[country] || '🌐';
  };

  const getTypeColor = (type) => {
    const colors = {
      'APT': '#ea4335',
      'Ransomware': '#ff6d01',
      'Cybercrime': '#fbbc04'
    };
    return colors[type] || '#a1a1aa';
  };

  return (
    <div className="card">
      <div className="card-title">🎭 Threat Actor Activity</div>
      {actors.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '40px', color: '#a1a1aa' }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>🕵️</div>
          <div>No threat actor activity detected</div>
        </div>
      ) : (
        <div style={{ maxHeight: '600px', overflowY: 'auto' }}>
          {actors.map((actor, idx) => (
            <div 
              key={idx}
              style={{
                padding: '16px',
                margin: '12px 0',
                background: '#1e1e2e',
                borderRadius: '8px',
                borderLeft: `4px solid ${getTypeColor(actor.type)}`,
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
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                    <span style={{ fontSize: '20px' }}>{getCountryFlag(actor.country)}</span>
                    <span style={{ 
                      fontWeight: '700', 
                      fontSize: '16px',
                      color: '#e4e4e7'
                    }}>
                      {actor.actor}
                    </span>
                    <span style={{
                      padding: '2px 8px',
                      borderRadius: '4px',
                      fontSize: '11px',
                      fontWeight: '600',
                      background: `${getTypeColor(actor.type)}20`,
                      color: getTypeColor(actor.type)
                    }}>
                      {actor.type}
                    </span>
                  </div>
                  <div style={{ 
                    fontSize: '12px', 
                    color: '#a1a1aa',
                    marginBottom: '8px'
                  }}>
                    {actor.country}
                  </div>
                </div>
                <div style={{ 
                  fontSize: '11px', 
                  color: '#a1a1aa',
                  whiteSpace: 'nowrap'
                }}>
                  {new Date(actor.date).toLocaleDateString()}
                </div>
              </div>
              <div style={{ 
                fontSize: '13px', 
                color: '#e0e0e0',
                lineHeight: '1.5'
              }}>
                {actor.article_title}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default ThreatActorActivity;
