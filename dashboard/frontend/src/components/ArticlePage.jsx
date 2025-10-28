import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useSearchParams } from 'react-router-dom';

const API_BASE = 'http://localhost:5000/api';

function ArticlePage() {
  const [searchParams] = useSearchParams();
  const articleId = searchParams.get('id');
  const [article, setArticle] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!articleId) {
      setError('No article ID provided');
      setLoading(false);
      return;
    }

    api.getArticle(articleId)
      .then(data => {
        const articleData = {
          ...data,
          iocs: data.iocs || [],
          kql_queries: data.kql_queries || [],
          summary: data.summary || '',
          recommendations: data.recommendations || '',
          source_url: data.source_url || '',
          category: data.category || 'Uncategorized',
          risk_level: data.risk_level || 'UNKNOWN'
        };
        setArticle(articleData);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error loading article:', err);
        setError('Failed to load article details');
        setLoading(false);
      });
  }, [articleId]);

  if (loading) {
    return (
      <div style={{ 
        minHeight: '100vh', 
        background: '#1e1e2e', 
        color: '#e4e4e7',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>⏳</div>
          <div>Loading article...</div>
        </div>
      </div>
    );
  }

  if (error || !article) {
    return (
      <div style={{ 
        minHeight: '100vh', 
        background: '#1e1e2e', 
        color: '#e4e4e7',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '48px', marginBottom: '16px', color: '#ea4335' }}>❌</div>
          <div style={{ color: '#ea4335' }}>{error || 'Article not found'}</div>
        </div>
      </div>
    );
  }

  return (
    <div style={{ 
      minHeight: '100vh', 
      background: '#1e1e2e', 
      color: '#e4e4e7',
      padding: '40px 20px'
    }}>
      <div style={{ 
        maxWidth: '1000px', 
        margin: '0 auto',
        background: '#2a2a3e',
        borderRadius: '12px',
        padding: '40px',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.3)'
      }}>
        {/* Header */}
        <div style={{ marginBottom: '24px' }}>
          <h1 style={{ 
            fontSize: '32px', 
            fontWeight: '700',
            marginBottom: '16px',
            color: '#4285f4',
            lineHeight: '1.3'
          }}>
            {article.title}
          </h1>
          <button 
            onClick={() => window.close()}
            style={{
              padding: '10px 20px',
              borderRadius: '6px',
              border: '2px solid #3a3a4a',
              background: '#1e1e2e',
              color: '#e0e0e0',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '600'
            }}
          >
            ← Back to Dashboard
          </button>
        </div>

        {/* Metadata Section */}
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '16px',
          padding: '20px',
          background: '#1e1e2e',
          borderRadius: '8px',
          marginBottom: '32px'
        }}>
          <div>
            <div style={{ color: '#a1a1aa', fontSize: '12px', marginBottom: '4px', textTransform: 'uppercase' }}>Risk Level</div>
            <div style={{ 
              display: 'inline-block',
              padding: '6px 16px',
              borderRadius: '6px',
              background: article.risk_level === 'HIGH' ? '#ea433520' : 
                         article.risk_level === 'MEDIUM' ? '#fbbc0420' : '#34a85320',
              color: article.risk_level === 'HIGH' ? '#ea4335' : 
                     article.risk_level === 'MEDIUM' ? '#fbbc04' : '#34a853',
              fontWeight: '700',
              fontSize: '14px'
            }}>
              {article.risk_level}
            </div>
          </div>
          <div>
            <div style={{ color: '#a1a1aa', fontSize: '12px', marginBottom: '4px', textTransform: 'uppercase' }}>Category</div>
            <div style={{ fontWeight: '600', color: '#4285f4', fontSize: '16px' }}>{article.category}</div>
          </div>
          <div>
            <div style={{ color: '#a1a1aa', fontSize: '12px', marginBottom: '4px', textTransform: 'uppercase' }}>Published</div>
            <div style={{ fontWeight: '500', fontSize: '16px' }}>{new Date(article.published_date).toLocaleDateString()}</div>
          </div>
          <div>
            <div style={{ color: '#a1a1aa', fontSize: '12px', marginBottom: '4px', textTransform: 'uppercase' }}>IOCs / KQL</div>
            <div style={{ fontWeight: '600', fontSize: '16px' }}>
              {article.iocs?.length || 0} IOCs • {article.kql_queries?.length || 0} KQL
            </div>
          </div>
        </div>

        {/* Source URL */}
        {article.source_url && (
          <div style={{ marginBottom: '32px' }}>
            <h3 style={{ color: '#4285f4', fontSize: '18px', marginBottom: '12px', fontWeight: '600' }}>🔗 Source</h3>
            <a 
              href={article.source_url} 
              target="_blank" 
              rel="noopener noreferrer"
              style={{ 
                color: '#4285f4', 
                textDecoration: 'none',
                wordBreak: 'break-all',
                fontSize: '14px'
              }}
            >
              {article.source_url}
            </a>
          </div>
        )}

        {/* Summary */}
        <div style={{ marginBottom: '32px' }}>
          <h3 style={{ color: '#4285f4', fontSize: '18px', marginBottom: '12px', fontWeight: '600' }}>📄 Summary</h3>
          {article.summary && article.summary !== 'Not analyzed - fetched only' ? (
            <p style={{ lineHeight: '1.8', color: '#e0e0e0', fontSize: '15px' }}>
              {String(article.summary)}
            </p>
          ) : (
            <p style={{ color: '#a1a1aa', fontStyle: 'italic' }}>
              No summary available (article not yet analyzed)
            </p>
          )}
        </div>

        {/* Recommendations */}
        <div style={{ marginBottom: '32px' }}>
          <h3 style={{ color: '#4285f4', fontSize: '18px', marginBottom: '12px', fontWeight: '600' }}>💡 Recommendations</h3>
          {article.recommendations && article.recommendations !== '[]' ? (
            <div style={{ 
              padding: '20px', 
              background: '#1e1e2e', 
              borderRadius: '8px',
              borderLeft: '4px solid #34a853'
            }}>
              {(() => {
                try {
                  const recs = typeof article.recommendations === 'string' 
                    ? JSON.parse(article.recommendations) 
                    : article.recommendations;
                  
                  if (Array.isArray(recs) && recs.length > 0) {
                    return (
                      <ul style={{ margin: 0, paddingLeft: '24px' }}>
                        {recs.map((rec, idx) => {
                          if (typeof rec === 'object' && rec !== null) {
                            return (
                              <li key={idx} style={{ marginBottom: '12px', lineHeight: '1.6', fontSize: '14px' }}>
                                {rec.title && <strong>{rec.title}: </strong>}
                                {rec.description || JSON.stringify(rec)}
                              </li>
                            );
                          }
                          return <li key={idx} style={{ marginBottom: '12px', lineHeight: '1.6', fontSize: '14px' }}>{String(rec)}</li>;
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
          ) : (
            <p style={{ color: '#a1a1aa', fontStyle: 'italic' }}>
              No recommendations available
            </p>
          )}
        </div>

        {/* IOCs Section - Grouped by Type */}
        <div style={{ marginBottom: '32px' }}>
          <h3 style={{ color: '#4285f4', fontSize: '18px', marginBottom: '12px', fontWeight: '600' }}>
            🎯 Indicators of Compromise ({article.iocs?.length || 0})
          </h3>
          {(() => {
            const iocs = Array.isArray(article.iocs) ? article.iocs : [];
            if (iocs.length === 0) {
              return (
                <p style={{ color: '#a1a1aa', fontStyle: 'italic' }}>
                  No IOCs extracted
                </p>
              );
            }
            // Group by normalized IOC type
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
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                {sortedKeys.map((key) => {
                  const isDomains = key === 'Domains';
                  if (isDomains) {
                    const domainValues = Array.from(new Set((groups[key] || []).map(i => i.ioc_value).filter(Boolean)));
                    const domainText = domainValues.join('\n');
                    return (
                      <div key={key} style={{ background: '#1e1e2e', borderRadius: '8px', padding: '16px', border: '1px solid #303042' }}>
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px', gap: '8px' }}>
                          <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px' }}>
                            <span style={{ color: '#00d9c0', fontWeight: 700, fontSize: '13px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>{key}</span>
                            <span style={{ color: '#a1a1aa', fontSize: '12px' }}>({domainValues.length})</span>
                          </div>
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
                      </div>
                    );
                  }
                  return (
                    <div key={key} style={{ background: '#1e1e2e', borderRadius: '8px', padding: '16px', border: '1px solid #303042' }}>
                      <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px', marginBottom: '10px' }}>
                        <span style={{ color: '#00d9c0', fontWeight: 700, fontSize: '13px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>{key}</span>
                        <span style={{ color: '#a1a1aa', fontSize: '12px' }}>({groups[key].length})</span>
                      </div>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                        {groups[key].map((ioc, idx) => (
                          <div key={idx} style={{
                            background: '#2a2a3e',
                            color: '#e0e0e0',
                            fontFamily: 'monospace',
                            fontSize: '12px',
                            padding: '6px 8px',
                            borderRadius: '6px',
                            border: '1px solid #3a3a4a',
                            maxWidth: '100%',
                            overflowWrap: 'anywhere'
                          }}>
                            {ioc.ioc_value}
                            {/* Keep context for non-domain types only */}
                            {ioc.context && (
                              <span style={{ color: '#a1a1aa', fontSize: '11px' }}> • {ioc.context}</span>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  );
                })}
              </div>
            );
          })()}
        </div>

        {/* KQL Queries Section */}
        <div style={{ marginBottom: '32px' }}>
          <h3 style={{ color: '#4285f4', fontSize: '18px', marginBottom: '12px', fontWeight: '600' }}>
            📊 KQL Threat Hunting Queries ({article.kql_queries?.length || 0})
          </h3>
          {article.kql_queries && article.kql_queries.length > 0 ? (
            <div>
              {article.kql_queries.map((query, idx) => (
                <div key={idx} style={{ marginBottom: '20px' }}>
                  <div style={{ 
                    padding: '16px',
                    background: '#353549',
                    borderRadius: '8px 8px 0 0',
                    borderBottom: '3px solid #4285f4'
                  }}>
                    <div style={{ fontWeight: '700', color: '#4285f4', marginBottom: '6px', fontSize: '16px' }}>
                      {query.query_name}
                    </div>
                    <div style={{ fontSize: '12px', color: '#a1a1aa' }}>
                      Type: {query.query_type} • Platform: {query.platform || 'Defender/Sentinel'}
                    </div>
                  </div>
                  <pre style={{ 
                    background: '#1e1e2e', 
                    padding: '20px', 
                    borderRadius: '0 0 8px 8px',
                    overflow: 'auto',
                    fontSize: '13px',
                    margin: 0,
                    fontFamily: 'monospace',
                    color: '#e0e0e0',
                    lineHeight: '1.5',
                    whiteSpace: 'pre-wrap',
                    wordBreak: 'break-word',
                    overflowWrap: 'anywhere'
                  }}>
                    {query.kql_query || query.query_text}
                  </pre>
                </div>
              ))}
            </div>
          ) : (
            <p style={{ color: '#a1a1aa', fontStyle: 'italic' }}>
              No KQL queries generated
            </p>
          )}
        </div>

        {/* Not Analyzed Warning */}
        {(!article.summary || article.summary === 'Not analyzed - fetched only') && (
          <div style={{
            padding: '20px',
            background: '#fbbc0420',
            border: '2px solid #fbbc04',
            borderRadius: '8px',
            color: '#fbbc04',
            fontSize: '14px'
          }}>
            ⚠️ <strong>Note:</strong> This article has been fetched but not yet analyzed. 
            Run the analysis pipeline to extract IOCs, generate KQL queries, and get recommendations.
          </div>
        )}
      </div>
    </div>
  );
}

export default ArticlePage;
