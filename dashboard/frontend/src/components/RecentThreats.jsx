import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = 'http://localhost:5000/api';

function RecentThreats({ timeRange }) {
  const [threats, setThreats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedThreat, setSelectedThreat] = useState(null);
  const [modalLoading, setModalLoading] = useState(false);
  const [severityFilter, setSeverityFilter] = useState('ALL');

  useEffect(() => {
    setLoading(true);
    const riskParam = severityFilter === 'ALL' ? '' : `&risk=${severityFilter}`;
    
    // Build time range parameters
    let timeParams = '';
    if (timeRange.type === 'daterange' && timeRange.startDate && timeRange.endDate) {
      timeParams = `&start_date=${timeRange.startDate}&end_date=${timeRange.endDate}`;
    } else if (timeRange.days) {
      timeParams = `&days=${timeRange.days}`;
    }
    
    const url = `${API_BASE}/recent-threats?limit=50${riskParam}${timeParams}`;
    console.log('Fetching Recent Threats:', url);
    
    axios.get(url)
      .then(res => {
        console.log('Recent Threats Response:', res.data);
        setThreats(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error fetching recent threats:', err);
        setLoading(false);
      });
  }, [severityFilter, timeRange]);

  const handleThreatClick = (threatId) => {
    console.log('Article clicked, ID:', threatId);
    setModalLoading(true);
    setSelectedThreat({ id: threatId }); // Show modal immediately with loading state
    
    const url = `${API_BASE}/article/${threatId}`;
    console.log('Fetching article details:', url);
    
    axios.get(url)
      .then(res => {
        console.log('Article details received:', res.data);
        // Ensure data is properly formatted
        const articleData = {
          ...res.data,
          iocs: res.data.iocs || [],
          kql_queries: res.data.kql_queries || [],
          summary: res.data.summary || '',
          recommendations: res.data.recommendations || '',
          source_url: res.data.source_url || '',
          category: res.data.category || 'Uncategorized',
          risk_level: res.data.risk_level || 'UNKNOWN'
        };
        setSelectedThreat(articleData);
        setModalLoading(false);
      })
      .catch(err => {
        console.error('Error loading article details:', err);
        console.error('Error response:', err.response);
        setModalLoading(false);
        setSelectedThreat(null);
        alert('Failed to load article details. Check console for errors.');
      });
  };

  const closeModal = () => {
    setSelectedThreat(null);
    setModalLoading(false);
  };

  if (loading) return <div className="card loading">Loading threats...</div>;

  return (
    <div className="card">
      <div className="card-title">
        <span>🔥 Recent Threats</span>
        <div style={{ display: 'flex', gap: '8px', marginTop: '12px', flexWrap: 'wrap' }}>
          {['ALL', 'HIGH', 'MEDIUM', 'LOW', 'INFORMATIONAL'].map(level => (
            <button
              key={level}
              onClick={() => setSeverityFilter(level)}
              style={{
                padding: '6px 16px',
                borderRadius: '6px',
                border: severityFilter === level ? '2px solid #4285f4' : '2px solid #3a3a4a',
                background: severityFilter === level ? '#4285f420' : '#2a2a3a',
                color: severityFilter === level ? '#4285f4' : '#a1a1aa',
                cursor: 'pointer',
                fontSize: '12px',
                fontWeight: severityFilter === level ? '600' : '400',
                transition: 'all 0.2s ease'
              }}
              onMouseEnter={(e) => {
                if (severityFilter !== level) {
                  e.target.style.background = '#3a3a4a';
                }
              }}
              onMouseLeave={(e) => {
                if (severityFilter !== level) {
                  e.target.style.background = '#2a2a3a';
                }
              }}
            >
              {level}
            </button>
          ))}
        </div>
      </div>
      
      <div style={{ marginTop: '16px', maxHeight: '600px', overflowY: 'auto' }}>
        {threats.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px', color: '#a1a1aa' }}>
            <div style={{ fontSize: '48px', marginBottom: '16px' }}>📭</div>
            <div style={{ fontSize: '16px', fontWeight: '600', marginBottom: '8px' }}>
              No threats found
            </div>
            <div style={{ fontSize: '14px' }}>
              {severityFilter !== 'ALL' 
                ? `No ${severityFilter} severity threats in the selected time range`
                : 'No threats in the selected time range'}
            </div>
            <div style={{ fontSize: '12px', marginTop: '12px', color: '#666' }}>
              Try adjusting the time range filter or severity level
            </div>
          </div>
        ) : (
          threats.map(threat => (
            <div 
              key={threat.id} 
              className="threat-card"
              onClick={() => handleThreatClick(threat.id)}
              style={{ cursor: 'pointer' }}
            >
              <div className="threat-header">
                <span className={`risk-badge ${threat.risk_level}`}>
                  {threat.risk_level}
                </span>
                <div className="threat-title">{threat.title}</div>
              </div>
              <div className="threat-meta">
                <span className="category-tag">{threat.category}</span>
                <span>📅 {new Date(threat.published_date).toLocaleDateString()}</span>
                <span>🎯 {threat.ioc_count} IOCs</span>
                <span>📊 {threat.kql_count} KQL</span>
              </div>
            </div>
          ))
        )}
      </div>

      {selectedThreat && (
        <div className="modal" onClick={closeModal}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            {modalLoading ? (
              <div style={{ textAlign: 'center', padding: '40px' }}>
                <div style={{ fontSize: '24px', marginBottom: '16px' }}>⏳</div>
                <div style={{ color: '#a1a1aa' }}>Loading article details...</div>
              </div>
            ) : !selectedThreat ? (
              <div style={{ textAlign: 'center', padding: '40px' }}>
                <div style={{ fontSize: '24px', marginBottom: '16px', color: '#ea4335' }}>❌</div>
                <div style={{ color: '#ea4335' }}>Failed to load article details</div>
                <button 
                  onClick={closeModal}
                  style={{
                    padding: '8px 16px',
                    borderRadius: '6px',
                    border: '2px solid #3a3a4a',
                    background: '#2a2a3a',
                    color: '#e0e0e0',
                    cursor: 'pointer',
                    fontSize: '14px',
                    fontWeight: '600',
                    marginTop: '16px'
                  }}
                >
                  Close
                </button>
              </div>
            ) : (
              <>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '16px' }}>
                  <h2 style={{ margin: 0, flex: 1, paddingRight: '20px' }}>{selectedThreat.title}</h2>
                  <button 
                    onClick={closeModal}
                    style={{
                      padding: '8px 16px',
                      borderRadius: '6px',
                      border: '2px solid #3a3a4a',
                      background: '#2a2a3a',
                      color: '#e0e0e0',
                      cursor: 'pointer',
                      fontSize: '14px',
                      fontWeight: '600'
                    }}
                  >
                    ✕ Close
                  </button>
                </div>

                {/* Metadata Section */}
                <div style={{ 
                  display: 'grid', 
                  gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                  gap: '16px',
                  padding: '16px',
                  background: '#1e1e2e',
                  borderRadius: '8px',
                  marginBottom: '24px'
                }}>
                  <div>
                    <div style={{ color: '#a1a1aa', fontSize: '12px', marginBottom: '4px' }}>Risk Level</div>
                    <div style={{ 
                      display: 'inline-block',
                      padding: '4px 12px',
                      borderRadius: '4px',
                      background: selectedThreat.risk_level === 'HIGH' ? '#ea433520' : 
                                 selectedThreat.risk_level === 'MEDIUM' ? '#fbbc0420' : '#34a85320',
                      color: selectedThreat.risk_level === 'HIGH' ? '#ea4335' : 
                             selectedThreat.risk_level === 'MEDIUM' ? '#fbbc04' : '#34a853',
                      fontWeight: '600',
                      fontSize: '14px'
                    }}>
                      {selectedThreat.risk_level}
                    </div>
                  </div>
                  <div>
                    <div style={{ color: '#a1a1aa', fontSize: '12px', marginBottom: '4px' }}>Category</div>
                    <div style={{ fontWeight: '500', color: '#4285f4' }}>{selectedThreat.category}</div>
                  </div>
                  <div>
                    <div style={{ color: '#a1a1aa', fontSize: '12px', marginBottom: '4px' }}>Published</div>
                    <div style={{ fontWeight: '500' }}>{new Date(selectedThreat.published_date).toLocaleDateString()}</div>
                  </div>
                  <div>
                    <div style={{ color: '#a1a1aa', fontSize: '12px', marginBottom: '4px' }}>IOCs / KQL</div>
                    <div style={{ fontWeight: '500' }}>
                      {selectedThreat.iocs?.length || 0} IOCs • {selectedThreat.kql_queries?.length || 0} KQL
                    </div>
                  </div>
                </div>

                {/* Source URL */}
                {selectedThreat.source_url && (
                  <div style={{ marginBottom: '24px' }}>
                    <h3 style={{ color: '#4285f4', fontSize: '16px', marginBottom: '8px' }}>🔗 Source</h3>
                    <a 
                      href={selectedThreat.source_url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      style={{ 
                        color: '#4285f4', 
                        textDecoration: 'none',
                        wordBreak: 'break-all'
                      }}
                    >
                      {selectedThreat.source_url}
                    </a>
                  </div>
                )}

                {/* Summary */}
                {selectedThreat.summary && selectedThreat.summary !== 'Not analyzed - fetched only' ? (
                  <div style={{ marginBottom: '24px' }}>
                    <h3 style={{ color: '#4285f4', fontSize: '16px', marginBottom: '8px' }}>📄 Summary</h3>
                    <p style={{ lineHeight: '1.6', color: '#e0e0e0' }}>
                      {String(selectedThreat.summary)}
                    </p>
                  </div>
                ) : (
                  <div style={{ marginBottom: '24px' }}>
                    <h3 style={{ color: '#4285f4', fontSize: '16px', marginBottom: '8px' }}>📄 Summary</h3>
                    <p style={{ color: '#a1a1aa', fontStyle: 'italic' }}>
                      No summary available (article not yet analyzed)
                    </p>
                  </div>
                )}

                {/* Recommendations */}
                {selectedThreat.recommendations && selectedThreat.recommendations !== '[]' ? (
                  <div style={{ marginBottom: '24px' }}>
                    <h3 style={{ color: '#4285f4', fontSize: '16px', marginBottom: '8px' }}>💡 Recommendations</h3>
                    <div style={{ 
                      padding: '16px', 
                      background: '#1e1e2e', 
                      borderRadius: '8px',
                      borderLeft: '4px solid #34a853'
                    }}>
                      {(() => {
                        try {
                          const recs = typeof selectedThreat.recommendations === 'string' 
                            ? JSON.parse(selectedThreat.recommendations) 
                            : selectedThreat.recommendations;
                          
                          if (Array.isArray(recs) && recs.length > 0) {
                            return (
                              <ul style={{ margin: 0, paddingLeft: '20px' }}>
                                {recs.map((rec, idx) => {
                                  // Handle if rec is an object with title/description
                                  if (typeof rec === 'object' && rec !== null) {
                                    return (
                                      <li key={idx} style={{ marginBottom: '8px', lineHeight: '1.6' }}>
                                        {rec.title && <strong>{rec.title}: </strong>}
                                        {rec.description || JSON.stringify(rec)}
                                      </li>
                                    );
                                  }
                                  // Handle string recommendations
                                  return <li key={idx} style={{ marginBottom: '8px', lineHeight: '1.6' }}>{String(rec)}</li>;
                                })}
                              </ul>
                            );
                          }
                          return <p style={{ margin: 0, color: '#a1a1aa' }}>No recommendations available</p>;
                        } catch (e) {
                          console.error('Error parsing recommendations:', e);
                          return <p style={{ margin: 0, color: '#a1a1aa' }}>Error displaying recommendations</p>;
                        }
                      })()}
                    </div>
                  </div>
                ) : (
                  <div style={{ marginBottom: '24px' }}>
                    <h3 style={{ color: '#4285f4', fontSize: '16px', marginBottom: '8px' }}>💡 Recommendations</h3>
                    <p style={{ color: '#a1a1aa', fontStyle: 'italic' }}>
                      No recommendations available (article not yet analyzed)
                    </p>
                  </div>
                )}

                {/* IOCs Section */}
                {selectedThreat.iocs && selectedThreat.iocs.length > 0 ? (
                  <div style={{ marginBottom: '24px' }}>
                    <h3 style={{ color: '#4285f4', fontSize: '16px', marginBottom: '12px' }}>
                      🎯 Indicators of Compromise ({selectedThreat.iocs.length})
                    </h3>
                    <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
                      {selectedThreat.iocs.map((ioc, idx) => (
                        <div 
                          key={idx} 
                          style={{
                            padding: '12px',
                            backgroundColor: '#1e1e2e',
                            margin: '8px 0',
                            borderRadius: '6px',
                            borderLeft: '3px solid #00d9c0'
                          }}
                        >
                          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                            <span style={{ 
                              color: '#00d9c0', 
                              fontWeight: '600',
                              fontSize: '12px',
                              textTransform: 'uppercase'
                            }}>
                              {ioc.ioc_type}
                            </span>
                          </div>
                          <div style={{ 
                            color: '#e0e0e0', 
                            fontFamily: 'monospace',
                            fontSize: '13px',
                            wordBreak: 'break-all'
                          }}>
                            {ioc.ioc_value}
                          </div>
                          {ioc.context && (
                            <div style={{ 
                              color: '#a1a1aa', 
                              fontSize: '11px',
                              marginTop: '6px',
                              fontStyle: 'italic'
                            }}>
                              Context: {ioc.context}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div style={{ marginBottom: '24px' }}>
                    <h3 style={{ color: '#4285f4', fontSize: '16px', marginBottom: '8px' }}>🎯 IOCs</h3>
                    <p style={{ color: '#a1a1aa', fontStyle: 'italic' }}>
                      No IOCs extracted (article may not be fully analyzed)
                    </p>
                  </div>
                )}

                {/* KQL Queries Section */}
                {selectedThreat.kql_queries && selectedThreat.kql_queries.length > 0 ? (
                  <div style={{ marginBottom: '24px' }}>
                    <h3 style={{ color: '#4285f4', fontSize: '16px', marginBottom: '12px' }}>
                      📊 KQL Threat Hunting Queries ({selectedThreat.kql_queries.length})
                    </h3>
                    {selectedThreat.kql_queries.map((query, idx) => (
                      <div key={idx} style={{ marginBottom: '16px' }}>
                        <div style={{ 
                          padding: '12px',
                          background: '#2a2a3a',
                          borderRadius: '6px 6px 0 0',
                          borderBottom: '2px solid #4285f4'
                        }}>
                          <div style={{ fontWeight: '600', color: '#4285f4', marginBottom: '4px' }}>
                            {query.query_name}
                          </div>
                          <div style={{ fontSize: '12px', color: '#a1a1aa' }}>
                            Type: {query.query_type} • Platform: {query.platform || 'Defender/Sentinel'}
                          </div>
                        </div>
                        <pre style={{ 
                          background: '#1e1e2e', 
                          padding: '16px', 
                          borderRadius: '0 0 6px 6px',
                          overflow: 'auto',
                          fontSize: '12px',
                          margin: 0,
                          maxHeight: '200px',
                          fontFamily: 'monospace',
                          color: '#e0e0e0'
                        }}>
                          {query.kql_query || query.query_text}
                        </pre>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div style={{ marginBottom: '24px' }}>
                    <h3 style={{ color: '#4285f4', fontSize: '16px', marginBottom: '8px' }}>📊 KQL Queries</h3>
                    <p style={{ color: '#a1a1aa', fontStyle: 'italic' }}>
                      No KQL queries generated (article may not be fully analyzed)
                    </p>
                  </div>
                )}

                {/* Not Analyzed Warning */}
                {(!selectedThreat.summary || selectedThreat.summary === 'Not analyzed - fetched only') && (
                  <div style={{
                    padding: '16px',
                    background: '#fbbc0420',
                    border: '2px solid #fbbc04',
                    borderRadius: '8px',
                    color: '#fbbc04',
                    marginTop: '24px'
                  }}>
                    ⚠️ <strong>Note:</strong> This article has been fetched but not yet analyzed. 
                    Run the analysis pipeline to extract IOCs, generate KQL queries, and get recommendations.
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default RecentThreats;
