import React, { useState, useEffect } from 'react';
import api from '../utils/api';
import {
  ComposableMap,
  Geographies,
  Geography,
  Marker,
  ZoomableGroup
} from 'react-simple-maps';

// World topology data URL
const geoUrl = "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json";

function ThreatActorGeoMap({ timeRange }) {
  const [actors, setActors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedType, setSelectedType] = useState('ALL');
  const [hoveredActor, setHoveredActor] = useState(null);
  const [actorStats, setActorStats] = useState({});

  useEffect(() => {
    // Build time range parameters
    let timeParams = '';
    if (timeRange.type === 'daterange' && timeRange.startDate && timeRange.endDate) {
      timeParams = `?start_date=${timeRange.startDate}&end_date=${timeRange.endDate}`;
    } else if (timeRange.days) {
      timeParams = `?days=${timeRange.days}`;
    }
    
    api.getThreatActorActivity({})
      .then(data => {
        setActors(data);
        
        // Backend now returns aggregated data with incident_count
        // Convert to stats format for component compatibility
        const stats = {};
        data.forEach(actor => {
          const key = `${actor.actor}-${actor.country}`;
          stats[key] = {
            actor: actor.actor,
            country: actor.country,
            type: actor.type,
            lat: actor.lat,
            lon: actor.lon,
            count: actor.incident_count || 1,
            articles: actor.articles || []
          };
        });
        
        setActorStats(stats);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, [timeRange]);

  const getTypeColor = (type) => {
    const colors = {
      'APT': '#ea4335',
      'Ransomware': '#ff6d01',
      'Cybercrime': '#fbbc04',
      'Hacktivist': '#34a853'
    };
    return colors[type] || '#a1a1aa';
  };

  const getMarkerSize = (count) => {
    // Scale marker size based on incident count
    return Math.min(Math.max(count * 3, 8), 30);
  };

  const filteredActors = Object.values(actorStats).filter(actor => {
    if (selectedType === 'ALL') return true;
    return actor.type === selectedType;
  });

  if (loading) return <div className="card loading">Loading geo map...</div>;

  return (
    <div className="card">
      <div className="card-title" style={{ marginBottom: '16px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
          <span>🗺️ Threat Actor Geographic Activity</span>
          
          {/* Type Filter */}
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            {['ALL', 'APT', 'Ransomware', 'Cybercrime', 'Hacktivist'].map(type => (
              <button
                key={type}
                onClick={() => setSelectedType(type)}
                style={{
                  padding: '6px 14px',
                  borderRadius: '6px',
                  border: selectedType === type ? `2px solid ${type === 'ALL' ? '#4285f4' : getTypeColor(type)}` : '2px solid #3a3a4a',
                  background: selectedType === type ? `${type === 'ALL' ? '#4285f4' : getTypeColor(type)}20` : '#2a2a3a',
                  color: selectedType === type ? (type === 'ALL' ? '#4285f4' : getTypeColor(type)) : '#a1a1aa',
                  cursor: 'pointer',
                  fontSize: '12px',
                  fontWeight: selectedType === type ? '600' : '400',
                  transition: 'all 0.2s ease'
                }}
              >
                {type}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Legend */}
      <div style={{ 
        display: 'flex', 
        gap: '20px', 
        marginBottom: '16px', 
        padding: '12px', 
        background: '#1e1e2e', 
        borderRadius: '8px',
        flexWrap: 'wrap',
        fontSize: '12px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: getTypeColor('APT') }}></div>
          <span style={{ color: '#e4e4e7' }}>APT</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: getTypeColor('Ransomware') }}></div>
          <span style={{ color: '#e4e4e7' }}>Ransomware</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: getTypeColor('Cybercrime') }}></div>
          <span style={{ color: '#e4e4e7' }}>Cybercrime</span>
        </div>
        <div style={{ marginLeft: 'auto', color: '#a1a1aa' }}>
          📍 Marker size = incident count • Hover for details
        </div>
      </div>

      {filteredActors.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '60px', color: '#a1a1aa' }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>🌍</div>
          <div>No threat actor activity detected</div>
        </div>
      ) : (
        <div style={{ position: 'relative' }}>
          <ComposableMap
            projection="geoMercator"
            projectionConfig={{
              scale: 130
            }}
            style={{
              width: '100%',
              height: '500px'
            }}
          >
            <ZoomableGroup>
              <Geographies geography={geoUrl}>
                {({ geographies }) =>
                  geographies.map((geo) => (
                    <Geography
                      key={geo.rsmKey}
                      geography={geo}
                      fill="#2a2a3e"
                      stroke="#3a3a4a"
                      strokeWidth={0.5}
                      style={{
                        default: { outline: 'none' },
                        hover: { fill: '#353549', outline: 'none' },
                        pressed: { outline: 'none' }
                      }}
                    />
                  ))
                }
              </Geographies>

              {/* Markers for threat actors */}
              {filteredActors.map((actor, idx) => {
                if (actor.lat === 0 && actor.lon === 0) return null; // Skip unknown locations
                
                return (
                  <Marker
                    key={`${actor.actor}-${idx}`}
                    coordinates={[actor.lon, actor.lat]}
                    onMouseEnter={() => setHoveredActor(actor)}
                    onMouseLeave={() => setHoveredActor(null)}
                  >
                    <circle
                      r={getMarkerSize(actor.count)}
                      fill={getTypeColor(actor.type)}
                      fillOpacity={0.7}
                      stroke="#fff"
                      strokeWidth={2}
                      style={{
                        cursor: 'pointer',
                        transition: 'all 0.3s'
                      }}
                    />
                    {/* Pulsing effect for high activity */}
                    {actor.count > 5 && (
                      <circle
                        r={getMarkerSize(actor.count) + 5}
                        fill={getTypeColor(actor.type)}
                        fillOpacity={0.3}
                        style={{
                          animation: 'pulse 2s infinite'
                        }}
                      />
                    )}
                  </Marker>
                );
              })}
            </ZoomableGroup>
          </ComposableMap>

          {/* Tooltip */}
          {hoveredActor && (
            <div style={{
              position: 'absolute',
              top: '20px',
              right: '20px',
              background: '#2a2a3e',
              border: `2px solid ${getTypeColor(hoveredActor.type)}`,
              borderRadius: '8px',
              padding: '16px',
              minWidth: '280px',
              maxWidth: '350px',
              boxShadow: '0 4px 12px rgba(0, 0, 0, 0.5)',
              zIndex: 1000
            }}>
              <div style={{ 
                fontWeight: '700', 
                fontSize: '16px', 
                color: getTypeColor(hoveredActor.type),
                marginBottom: '8px',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}>
                <div style={{
                  width: '10px',
                  height: '10px',
                  borderRadius: '50%',
                  background: getTypeColor(hoveredActor.type)
                }}></div>
                {hoveredActor.actor}
              </div>
              <div style={{ fontSize: '13px', color: '#a1a1aa', marginBottom: '8px' }}>
                {hoveredActor.country} • {hoveredActor.type}
              </div>
              <div style={{ fontSize: '14px', color: '#e4e4e7', marginBottom: '8px', fontWeight: '600' }}>
                📊 {hoveredActor.count} incident{hoveredActor.count > 1 ? 's' : ''} detected
              </div>
              <div style={{ fontSize: '12px', color: '#a1a1aa', marginTop: '12px', paddingTop: '12px', borderTop: '1px solid #3a3a4a' }}>
                Recent Articles:
              </div>
              <div style={{ maxHeight: '120px', overflowY: 'auto', marginTop: '8px' }}>
                {hoveredActor.articles.slice(0, 3).map((article, idx) => (
                  <div key={idx} style={{ 
                    fontSize: '11px', 
                    color: '#e0e0e0', 
                    marginBottom: '6px',
                    paddingLeft: '8px',
                    borderLeft: '2px solid #3a3a4a'
                  }}>
                    • {article.title.substring(0, 60)}{article.title.length > 60 ? '...' : ''}
                  </div>
                ))}
                {hoveredActor.articles.length > 3 && (
                  <div style={{ fontSize: '11px', color: '#4285f4', marginTop: '4px' }}>
                    +{hoveredActor.articles.length - 3} more articles
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Summary Statistics */}
      <div style={{ 
        marginTop: '20px', 
        padding: '16px', 
        background: '#1e1e2e', 
        borderRadius: '8px',
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
        gap: '16px'
      }}>
        <div>
          <div style={{ fontSize: '24px', fontWeight: '700', color: '#4285f4' }}>
            {filteredActors.length}
          </div>
          <div style={{ fontSize: '12px', color: '#a1a1aa' }}>Active Actors</div>
        </div>
        <div>
          <div style={{ fontSize: '24px', fontWeight: '700', color: '#ea4335' }}>
            {filteredActors.reduce((sum, actor) => sum + actor.count, 0)}
          </div>
          <div style={{ fontSize: '12px', color: '#a1a1aa' }}>Total Incidents</div>
        </div>
        <div>
          <div style={{ fontSize: '24px', fontWeight: '700', color: '#ff6d01' }}>
            {new Set(filteredActors.map(a => a.country)).size}
          </div>
          <div style={{ fontSize: '12px', color: '#a1a1aa' }}>Countries</div>
        </div>
        <div>
          <div style={{ fontSize: '24px', fontWeight: '700', color: '#34a853' }}>
            {filteredActors.length > 0 ? filteredActors.sort((a, b) => b.count - a.count)[0].actor : 'N/A'}
          </div>
          <div style={{ fontSize: '12px', color: '#a1a1aa' }}>Most Active</div>
        </div>
      </div>

      {/* CSS for pulse animation */}
      <style>{`
        @keyframes pulse {
          0%, 100% {
            opacity: 0.3;
            transform: scale(1);
          }
          50% {
            opacity: 0.1;
            transform: scale(1.2);
          }
        }
      `}</style>
    </div>
  );
}

export default ThreatActorGeoMap;
