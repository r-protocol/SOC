import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = 'http://localhost:5000/api';

function RecentThreats({ timeRange }) {
  const [threats, setThreats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [severityFilter, setSeverityFilter] = useState('ALL');
  const [contextMenu, setContextMenu] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('date'); // date, title, risk, category
  const [sortOrder, setSortOrder] = useState('desc'); // asc, desc
  const [selectedArticle, setSelectedArticle] = useState(null);
  const [modalArticle, setModalArticle] = useState(null);
  const [modalLoading, setModalLoading] = useState(false);

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
    // Load article details in modal
    setModalLoading(true);
    setSelectedArticle(threatId);
    
    axios.get(`${API_BASE}/article/${threatId}`)
      .then(res => {
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
        setModalArticle(articleData);
        setModalLoading(false);
      })
      .catch(err => {
        console.error('Error fetching article:', err);
        setModalLoading(false);
        alert('Failed to load article details');
      });
  };

  const closeModal = () => {
    setSelectedArticle(null);
    setModalArticle(null);
    setModalLoading(false);
  };

  const handleContextMenu = (e, threat) => {
    e.preventDefault();
    setContextMenu({
      x: e.clientX,
      y: e.clientY,
      threat: threat
    });
  };

  const openSourceInNewTab = (threatId) => {
    // Get the article details and open source URL in new tab
    axios.get(`${API_BASE}/article/${threatId}`)
      .then(res => {
        if (res.data.source_url) {
          window.open(res.data.source_url, '_blank', 'noopener,noreferrer');
        } else {
          alert('No source URL available for this article');
        }
      })
      .catch(err => {
        console.error('Error fetching article for new tab:', err);
        alert('Failed to open article source');
      });
    setContextMenu(null);
  };

  // Filter and sort threats
  const getFilteredAndSortedThreats = () => {
    let filtered = threats;

    // Apply search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(threat => 
        threat.title.toLowerCase().includes(query) ||
        threat.category.toLowerCase().includes(query)
      );
    }

    // Apply sorting
    filtered = [...filtered].sort((a, b) => {
      let compareValue = 0;

      switch (sortBy) {
        case 'title':
          compareValue = a.title.localeCompare(b.title);
          break;
        case 'risk':
          const riskOrder = { HIGH: 4, MEDIUM: 3, LOW: 2, INFORMATIONAL: 1 };
          compareValue = (riskOrder[a.risk_level] || 0) - (riskOrder[b.risk_level] || 0);
          break;
        case 'category':
          compareValue = a.category.localeCompare(b.category);
          break;
        case 'date':
        default:
          compareValue = new Date(a.published_date) - new Date(b.published_date);
          break;
      }

      return sortOrder === 'asc' ? compareValue : -compareValue;
    });

    return filtered;
  };

  const toggleSortOrder = () => {
    setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc');
  };

  // Close context menu when clicking anywhere
  useEffect(() => {
    const handleClick = () => setContextMenu(null);
    if (contextMenu) {
      document.addEventListener('click', handleClick);
      return () => document.removeEventListener('click', handleClick);
    }
  }, [contextMenu]);

  // Close modal on Escape key
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape' && selectedArticle) {
        closeModal();
      }
    };
    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [selectedArticle]);

  const filteredThreats = getFilteredAndSortedThreats();

  if (loading) return <div className="card loading">Loading threats...</div>;

  return (
    <>
      <div className="card">
        <div className="card-title">
          <span>🔥 Recent Threats</span>
          
          {/* Severity Filter Buttons */}
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

        {/* Search and Sort Controls */}
        <div style={{ marginTop: '16px', display: 'flex', gap: '12px', flexWrap: 'wrap', alignItems: 'center' }}>
          {/* Search Input */}
          <div style={{ flex: '1', minWidth: '200px', position: 'relative' }}>
            <input
              type="text"
              placeholder="🔍 Search by title or category..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{
                width: '100%',
                padding: '10px 16px',
                borderRadius: '8px',
                border: '2px solid #3a3a4a',
                background: '#1e1e2e',
                color: '#e4e4e7',
                fontSize: '14px',
                outline: 'none',
                transition: 'border-color 0.2s'
              }}
              onFocus={(e) => e.target.style.borderColor = '#4285f4'}
              onBlur={(e) => e.target.style.borderColor = '#3a3a4a'}
            />
          </div>

          {/* Sort By Dropdown */}
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            <span style={{ color: '#a1a1aa', fontSize: '14px', fontWeight: '500' }}>Sort by:</span>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              style={{
                padding: '8px 12px',
                borderRadius: '6px',
                border: '2px solid #3a3a4a',
                background: '#1e1e2e',
                color: '#e4e4e7',
                fontSize: '14px',
                cursor: 'pointer',
                outline: 'none'
              }}
            >
              <option value="date">Date</option>
              <option value="title">Title</option>
              <option value="risk">Risk Level</option>
              <option value="category">Category</option>
            </select>

            {/* Sort Order Toggle */}
            <button
              onClick={toggleSortOrder}
              style={{
                padding: '8px 12px',
                borderRadius: '6px',
                border: '2px solid #3a3a4a',
                background: '#1e1e2e',
                color: '#e4e4e7',
                cursor: 'pointer',
                fontSize: '16px',
                lineHeight: '1',
                transition: 'all 0.2s'
              }}
              title={sortOrder === 'asc' ? 'Ascending' : 'Descending'}
            >
              {sortOrder === 'asc' ? '↑' : '↓'}
            </button>
          </div>

          {/* Results Count */}
          <div style={{ color: '#a1a1aa', fontSize: '14px', fontWeight: '500' }}>
            {filteredThreats.length} result{filteredThreats.length !== 1 ? 's' : ''}
          </div>
        </div>
        
        <div style={{ marginTop: '16px', maxHeight: '600px', overflowY: 'auto' }}>
          {filteredThreats.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '40px', color: '#a1a1aa' }}>
              <div style={{ fontSize: '48px', marginBottom: '16px' }}>📭</div>
              <div style={{ fontSize: '16px', fontWeight: '600', marginBottom: '8px' }}>
                No threats found
              </div>
              <div style={{ fontSize: '14px' }}>
                {searchQuery.trim() 
                  ? `No results for "${searchQuery}"`
                  : severityFilter !== 'ALL' 
                  ? `No ${severityFilter} severity threats in the selected time range`
                  : 'No threats in the selected time range'}
              </div>
              <div style={{ fontSize: '12px', marginTop: '12px', color: '#666' }}>
                Try adjusting the {searchQuery.trim() ? 'search query, ' : ''}time range filter or severity level
              </div>
            </div>
          ) : (
            filteredThreats.map(threat => (
              <div 
                key={threat.id} 
                className="threat-card"
                onClick={() => handleThreatClick(threat.id)}
                onContextMenu={(e) => handleContextMenu(e, threat)}
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

        {/* Context Menu */}
        {contextMenu && (
          <div
            style={{
              position: 'fixed',
              top: contextMenu.y,
              left: contextMenu.x,
              background: '#2a2a3e',
              border: '1px solid #3f3f55',
              borderRadius: '6px',
              boxShadow: '0 4px 12px rgba(0, 0, 0, 0.5)',
              zIndex: 10000,
              minWidth: '200px',
              overflow: 'hidden'
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div
              onClick={() => openSourceInNewTab(contextMenu.threat.id)}
              style={{
                padding: '12px 16px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                color: '#e4e4e7',
                fontSize: '14px',
                transition: 'background 0.2s'
              }}
              onMouseEnter={(e) => e.target.style.background = '#353549'}
              onMouseLeave={(e) => e.target.style.background = 'transparent'}
            >
              <span>🔗</span>
              <span>Open Source URL</span>
            </div>
            <div
              onClick={() => {
                handleThreatClick(contextMenu.threat.id);
                setContextMenu(null);
              }}
              style={{
                padding: '12px 16px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                color: '#e4e4e7',
                fontSize: '14px',
                borderTop: '1px solid #3f3f55',
                transition: 'background 0.2s'
              }}
              onMouseEnter={(e) => e.target.style.background = '#353549'}
              onMouseLeave={(e) => e.target.style.background = 'transparent'}
            >
              <span>📋</span>
              <span>View Full Article</span>
            </div>
          </div>
        )}
      </div>

      {/* Modal - 65% Screen Coverage */}
      {selectedArticle && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            width: '100vw',
            height: '100vh',
            background: 'rgba(0, 0, 0, 0.85)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 9999,
            padding: '20px'
          }}
          onClick={closeModal}
        >
          <div
            style={{
              width: '65vw',
              maxWidth: '1200px',
              height: '85vh',
              background: '#2a2a3e',
              borderRadius: '16px',
              overflow: 'hidden',
              display: 'flex',
              flexDirection: 'column',
              boxShadow: '0 8px 32px rgba(0, 0, 0, 0.5)'
            }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div style={{
              padding: '20px 30px',
              background: '#1e1e2e',
              borderBottom: '2px solid #3a3a4a',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}>
              <h2 style={{ margin: 0, fontSize: '20px', color: '#4285f4', fontWeight: '600' }}>
                📄 Article Details
              </h2>
              <button
                onClick={closeModal}
                style={{
                  background: '#ea4335',
                  border: 'none',
                  color: 'white',
                  padding: '8px 16px',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '14px',
                  fontWeight: '600',
                  transition: 'background 0.2s'
                }}
                onMouseEnter={(e) => e.target.style.background = '#c53929'}
                onMouseLeave={(e) => e.target.style.background = '#ea4335'}
              >
                ✕ Close
              </button>
            </div>

            {/* Modal Content */}
            <div style={{
              flex: 1,
              overflow: 'auto',
              padding: '30px'
            }}>
              {modalLoading ? (
                <div style={{ textAlign: 'center', padding: '60px', color: '#a1a1aa' }}>
                  <div style={{ fontSize: '48px', marginBottom: '16px' }}>⏳</div>
                  <div>Loading article...</div>
                </div>
              ) : modalArticle ? (
                <>
                  {/* Article Title */}
                  <h1 style={{ 
                    fontSize: '28px', 
                    fontWeight: '700',
                    marginBottom: '20px',
                    color: '#e4e4e7',
                    lineHeight: '1.4'
                  }}>
                    {modalArticle.title}
                  </h1>

                  {/* Metadata */}
                  <div style={{ 
                    display: 'grid', 
                    gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
                    gap: '16px',
                    padding: '20px',
                    background: '#1e1e2e',
                    borderRadius: '8px',
                    marginBottom: '24px'
                  }}>
                    <div>
                      <div style={{ color: '#a1a1aa', fontSize: '11px', marginBottom: '6px', textTransform: 'uppercase', fontWeight: '600' }}>Risk Level</div>
                      <div style={{ 
                        display: 'inline-block',
                        padding: '6px 14px',
                        borderRadius: '6px',
                        background: modalArticle.risk_level === 'HIGH' ? '#ea433520' : 
                                   modalArticle.risk_level === 'MEDIUM' ? '#fbbc0420' : '#34a85320',
                        color: modalArticle.risk_level === 'HIGH' ? '#ea4335' : 
                               modalArticle.risk_level === 'MEDIUM' ? '#fbbc04' : '#34a853',
                        fontWeight: '700',
                        fontSize: '13px'
                      }}>
                        {modalArticle.risk_level}
                      </div>
                    </div>
                    <div>
                      <div style={{ color: '#a1a1aa', fontSize: '11px', marginBottom: '6px', textTransform: 'uppercase', fontWeight: '600' }}>Category</div>
                      <div style={{ fontWeight: '600', color: '#4285f4', fontSize: '15px' }}>{modalArticle.category}</div>
                    </div>
                    <div>
                      <div style={{ color: '#a1a1aa', fontSize: '11px', marginBottom: '6px', textTransform: 'uppercase', fontWeight: '600' }}>Published</div>
                      <div style={{ fontWeight: '500', fontSize: '15px', color: '#e4e4e7' }}>{new Date(modalArticle.published_date).toLocaleDateString()}</div>
                    </div>
                    <div>
                      <div style={{ color: '#a1a1aa', fontSize: '11px', marginBottom: '6px', textTransform: 'uppercase', fontWeight: '600' }}>IOCs / KQL</div>
                      <div style={{ fontWeight: '600', fontSize: '15px', color: '#e4e4e7' }}>
                        {modalArticle.iocs?.length || 0} IOCs • {modalArticle.kql_queries?.length || 0} KQL
                      </div>
                    </div>
                  </div>

                  {/* Source URL */}
                  {modalArticle.source_url && (
                    <div style={{ marginBottom: '24px' }}>
                      <h3 style={{ color: '#4285f4', fontSize: '16px', marginBottom: '10px', fontWeight: '600' }}>🔗 Source</h3>
                      <a 
                        href={modalArticle.source_url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        style={{ 
                          color: '#4285f4', 
                          textDecoration: 'none',
                          wordBreak: 'break-all',
                          fontSize: '14px'
                        }}
                      >
                        {modalArticle.source_url}
                      </a>
                    </div>
                  )}

                  {/* Summary */}
                  <div style={{ marginBottom: '24px' }}>
                    <h3 style={{ color: '#4285f4', fontSize: '16px', marginBottom: '10px', fontWeight: '600' }}>📄 Summary</h3>
                    {modalArticle.summary && modalArticle.summary !== 'Not analyzed - fetched only' ? (
                      <p style={{ lineHeight: '1.7', color: '#e0e0e0', fontSize: '14px' }}>
                        {String(modalArticle.summary)}
                      </p>
                    ) : (
                      <p style={{ color: '#a1a1aa', fontStyle: 'italic' }}>
                        No summary available (article not yet analyzed)
                      </p>
                    )}
                  </div>

                  {/* Recommendations */}
                  {modalArticle.recommendations && modalArticle.recommendations !== '[]' && (
                    <div style={{ marginBottom: '24px' }}>
                      <h3 style={{ color: '#4285f4', fontSize: '16px', marginBottom: '10px', fontWeight: '600' }}>💡 Recommendations</h3>
                      <div style={{ 
                        padding: '16px', 
                        background: '#1e1e2e', 
                        borderRadius: '8px',
                        borderLeft: '4px solid #34a853'
                      }}>
                        {(() => {
                          try {
                            const recs = typeof modalArticle.recommendations === 'string' 
                              ? JSON.parse(modalArticle.recommendations) 
                              : modalArticle.recommendations;
                            
                            if (Array.isArray(recs) && recs.length > 0) {
                              return (
                                <ul style={{ margin: 0, paddingLeft: '20px' }}>
                                  {recs.map((rec, idx) => {
                                    if (typeof rec === 'object' && rec !== null) {
                                      return (
                                        <li key={idx} style={{ marginBottom: '10px', lineHeight: '1.5', fontSize: '13px', color: '#e0e0e0' }}>
                                          {rec.title && <strong>{rec.title}: </strong>}
                                          {rec.description || JSON.stringify(rec)}
                                        </li>
                                      );
                                    }
                                    return <li key={idx} style={{ marginBottom: '10px', lineHeight: '1.5', fontSize: '13px', color: '#e0e0e0' }}>{String(rec)}</li>;
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
                  )}

                  {/* IOCs Section - Grouped by Type */}
                  {modalArticle.iocs && modalArticle.iocs.length > 0 && (
                    <div style={{ marginBottom: '24px' }}>
                      <h3 style={{ color: '#4285f4', fontSize: '16px', marginBottom: '10px', fontWeight: '600' }}>
                        🎯 Indicators of Compromise ({modalArticle.iocs.length})
                      </h3>
                      {(() => {
                        const iocs = Array.isArray(modalArticle.iocs) ? modalArticle.iocs : [];
                        const groups = {};
                        const labelFor = (t) => {
                          const s = String(t || '').toLowerCase();
                          if (s.includes('sender') && s.includes('domain')) return 'Sender Domains';
                          if (s.includes('sender')) return 'Sender Emails';
                          if (s.includes('email')) return 'Emails';
                          if (s.includes('domain')) return 'Domains';
                          if (s === 'ips' || s.includes('ip')) return 'IPs';
                          if (s.includes('url')) return 'URLs';
                          if (s.includes('hash') || s.includes('sha') || s.includes('md5')) return 'Hashes';
                          if (s.includes('cve')) return 'CVEs';
                          return (t || 'Other').toString();
                        };
                        const order = ['Domains', 'IPs', 'URLs', 'Sender Domains', 'Sender Emails', 'Emails', 'Hashes', 'CVEs'];
                        for (const ioc of iocs) {
                          const key = labelFor(ioc.ioc_type);
                          if (!groups[key]) groups[key] = [];
                          groups[key].push(ioc);
                        }
                        const sortedKeys = Object.keys(groups).sort((a, b) => {
                          const ia = order.indexOf(a);
                          const ib = order.indexOf(b);
                          if (ia === -1 && ib === -1) return a.localeCompare(b);
                          if (ia === -1) return 1;
                          if (ib === -1) return -1;
                          return ia - ib;
                        });
                        return (
                          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', maxHeight: '360px', overflowY: 'auto' }}>
                            {sortedKeys.map((key) => (
                              <div key={key} style={{ background: '#1e1e2e', borderRadius: '8px', padding: '12px', border: '1px solid #303042' }}>
                                <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px', marginBottom: '8px' }}>
                                  <span style={{ color: '#00d9c0', fontWeight: 700, fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>{key}</span>
                                  <span style={{ color: '#a1a1aa', fontSize: '11px' }}>({groups[key].length})</span>
                                </div>
                                {key === 'Domains' ? (
                                  (() => {
                                    const domainValues = Array.from(new Set((groups[key] || []).map(i => i.ioc_value).filter(Boolean)));
                                    const domainText = domainValues.join('\n');
                                    return (
                                      <>
                                        <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '8px' }}>
                                          <button
                                            onClick={() => navigator.clipboard?.writeText(domainText)}
                                            title="Copy domains to clipboard"
                                            style={{ padding: '6px 10px', borderRadius: '6px', border: '1px solid #3a3a4a', background: '#2a2a3e', color: '#e0e0e0', cursor: 'pointer', fontSize: '12px' }}
                                          >
                                            Copy
                                          </button>
                                        </div>
                                        <pre style={{
                                          background: '#2a2a3e',
                                          color: '#e0e0e0',
                                          fontFamily: 'monospace',
                                          fontSize: '12px',
                                          padding: '10px',
                                          borderRadius: '6px',
                                          border: '1px solid #3a3a4a',
                                          margin: 0,
                                          whiteSpace: 'pre-wrap',
                                          wordBreak: 'break-word',
                                          overflowWrap: 'anywhere'
                                        }}>{domainText}</pre>
                                      </>
                                    );
                                  })()
                                ) : (
                                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                                    {groups[key].map((ioc, idx) => (
                                      <div key={idx} style={{
                                        background: '#2a2a3e',
                                        color: '#e0e0e0',
                                        fontFamily: 'monospace',
                                        fontSize: '12px',
                                        padding: '5px 7px',
                                        borderRadius: '6px',
                                        border: '1px solid #3a3a4a',
                                        maxWidth: '100%',
                                        overflowWrap: 'anywhere'
                                      }}>
                                        {ioc.ioc_value}
                                        {ioc.context && (
                                          <span style={{ color: '#a1a1aa', fontSize: '11px' }}> • {ioc.context}</span>
                                        )}
                                      </div>
                                    ))}
                                  </div>
                                )}
                              </div>
                            ))}
                          </div>
                        );
                      })()}
                    </div>
                  )}

                  {/* KQL Queries Section */}
                  {modalArticle.kql_queries && modalArticle.kql_queries.length > 0 && (
                    <div style={{ marginBottom: '24px' }}>
                      <h3 style={{ color: '#4285f4', fontSize: '16px', marginBottom: '10px', fontWeight: '600' }}>
                        📊 KQL Threat Hunting Queries ({modalArticle.kql_queries.length})
                      </h3>
                      <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
                        {modalArticle.kql_queries.map((query, idx) => (
                          <div key={idx} style={{ marginBottom: '16px' }}>
                            <div style={{ 
                              padding: '12px',
                              background: '#353549',
                              borderRadius: '6px 6px 0 0',
                              borderBottom: '2px solid #4285f4'
                            }}>
                              <div style={{ fontWeight: '700', color: '#4285f4', marginBottom: '4px', fontSize: '14px' }}>
                                {query.query_name}
                              </div>
                              <div style={{ fontSize: '11px', color: '#a1a1aa' }}>
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
                              fontFamily: 'monospace',
                              color: '#e0e0e0',
                              lineHeight: '1.4',
                              maxHeight: '200px',
                              whiteSpace: 'pre-wrap',
                              wordBreak: 'break-word',
                              overflowWrap: 'anywhere'
                            }}>
                              {query.kql_query || query.query_text}
                            </pre>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </>
              ) : (
                <div style={{ textAlign: 'center', padding: '60px', color: '#a1a1aa' }}>
                  <div style={{ fontSize: '48px', marginBottom: '16px' }}>❌</div>
                  <div>Failed to load article</div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export default RecentThreats;
