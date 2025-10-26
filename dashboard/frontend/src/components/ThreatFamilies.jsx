import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = 'http://localhost:5000/api';

function ThreatFamilies() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get(`${API_BASE}/threat-families`)
      .then(res => {
        setData(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="card loading">Loading threat families...</div>;
  if (data.length === 0) return <div className="card">No threat families detected yet</div>;

  return (
    <div className="card">
      <div className="card-title">🦠 Common Threat Families</div>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px', justifyContent: 'center', minHeight: '250px', alignItems: 'center' }}>
        {data.map((item, idx) => (
          <span 
            key={idx}
            style={{
              fontSize: `${12 + item.value * 2}px`,
              color: ['#4285f4', '#ea4335', '#fbbc04', '#34a853', '#a142f4'][idx % 5],
              fontWeight: 600,
              padding: '8px'
            }}
          >
            {item.text}
          </span>
        ))}
      </div>
    </div>
  );
}

export default ThreatFamilies;
