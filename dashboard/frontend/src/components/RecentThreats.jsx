import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = 'http://localhost:5000/api';

function RecentThreats() {
  const [threats, setThreats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedThreat, setSelectedThreat] = useState(null);

  useEffect(() => {
    axios.get(`${API_BASE}/recent-threats?limit=20`)
      .then(res => {
        setThreats(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  const handleThreatClick = (threatId) => {
    axios.get(`${API_BASE}/article/${threatId}`)
      .then(res => {
        setSelectedThreat(res.data);
      });
  };

  if (loading) return <div className="card loading">Loading threats...</div>;

  return (
    <div className="card">
      <div className="card-title">🔥 Recent High-Priority Threats</div>
      {threats.map(threat => (
        <div 
          key={threat.id} 
          className="threat-card"
          onClick={() => handleThreatClick(threat.id)}
        >
          <div className="threat-header">
            <span className={`risk-badge ${threat.risk_level}`}>
              {threat.risk_level}
            </span>
            <div className="threat-title">{threat.title}</div>
          </div>
          <div className="threat-meta">
            <span className="category-tag">{threat.category}</span>
            <span>{new Date(threat.published_date).toLocaleDateString()}</span>
            <span>🎯 {threat.ioc_count} IOCs</span>
          </div>
        </div>
      ))}

      {selectedThreat && (
        <div className="modal" onClick={() => setSelectedThreat(null)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <h2>{selectedThreat.title}</h2>
            <p style={{marginTop: '16px', color: '#a1a1aa'}}><strong>Risk:</strong> {selectedThreat.risk_level}</p>
            <p style={{marginTop: '8px', color: '#a1a1aa'}}><strong>Category:</strong> {selectedThreat.category}</p>
            
            {selectedThreat.summary && (
              <>
                <h3 style={{marginTop: '24px', color: '#4285f4'}}>Summary</h3>
                <p style={{marginTop: '8px'}}>{selectedThreat.summary}</p>
              </>
            )}
            
            {selectedThreat.iocs && selectedThreat.iocs.length > 0 && (
              <>
                <h3 style={{marginTop: '24px', color: '#4285f4'}}>IOCs ({selectedThreat.iocs.length})</h3>
                <div style={{maxHeight: '200px', overflowY: 'auto'}}>
                  {selectedThreat.iocs.slice(0, 10).map((ioc, idx) => (
                    <div key={idx} style={{padding: '8px', backgroundColor: '#1e1e2e', margin: '4px 0', borderRadius: '4px'}}>
                      <span style={{color: '#00d9c0'}}>{ioc.ioc_type}:</span> {ioc.ioc_value}
                    </div>
                  ))}
                </div>
              </>
            )}
            
            {selectedThreat.kql_queries && selectedThreat.kql_queries.length > 0 && (
              <>
                <h3 style={{marginTop: '24px', color: '#4285f4'}}>KQL Queries ({selectedThreat.kql_queries.length})</h3>
                {selectedThreat.kql_queries.slice(0, 2).map((query, idx) => (
                  <div key={idx}>
                    <p style={{marginTop: '12px', fontWeight: 600}}>{query.query_name}</p>
                    <pre style={{ background: '#1e1e2e', padding: '16px', borderRadius: '8px', overflow: 'auto', fontSize: '11px' }}>
                      {query.query_text}
                    </pre>
                  </div>
                ))}
              </>
            )}
            
            <button onClick={() => setSelectedThreat(null)}>Close</button>
          </div>
        </div>
      )}
    </div>
  );
}

export default RecentThreats;
