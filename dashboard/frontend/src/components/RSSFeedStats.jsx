import React, { useState, useEffect } from 'react';
import api from '../utils/api';

function RSSFeedStats() {
  const [feeds, setFeeds] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getRSSFeedStats()
      .then(data => {
        setFeeds(data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="card loading">Loading RSS stats...</div>;

  return (
    <div className="card">
      <div className="card-title">📡 Source Intelligence Coverage</div>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr style={{ borderBottom: '1px solid #3f3f55' }}>
            <th style={{ padding: '12px', textAlign: 'left' }}>Feed</th>
            <th style={{ padding: '12px', textAlign: 'center' }}>Articles</th>
            <th style={{ padding: '12px', textAlign: 'center' }}>Parsed</th>
            <th style={{ padding: '12px', textAlign: 'center' }}>Status</th>
          </tr>
        </thead>
        <tbody>
          {feeds.map((feed, idx) => (
            <tr key={idx} style={{ borderBottom: '1px solid #3f3f55' }}>
              <td style={{ padding: '12px' }}>{feed.name}</td>
              <td style={{ padding: '12px', textAlign: 'center' }}>{feed.articles}</td>
              <td style={{ padding: '12px', textAlign: 'center' }}>{feed.parsed}</td>
              <td style={{ padding: '12px', textAlign: 'center' }}>✅</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default RSSFeedStats;
