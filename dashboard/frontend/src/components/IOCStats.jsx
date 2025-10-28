import React, { useState, useEffect } from 'react';
import api from '../utils/api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

function IOCStats() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getIOCStats()
      .then(data => {
        const formatted = [
          { name: 'Domains', count: data.domains, fill: '#4285f4' },
          { name: 'IPs', count: data.ips, fill: '#34a853' },
          { name: 'Hashes', count: data.hashes, fill: '#ff6d01' },
          { name: 'CVEs', count: data.cves, fill: '#ea4335' }
        ];
        setData(formatted);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="card loading">Loading IOC stats...</div>;

  return (
    <div className="card">
      <div className="card-title">🎯 IOC Breakdown</div>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#3f3f55" />
          <XAxis type="number" stroke="#a1a1aa" />
          <YAxis type="category" dataKey="name" stroke="#a1a1aa" width={80} />
          <Tooltip 
            contentStyle={{ backgroundColor: '#2a2a3e', border: '1px solid #3f3f55' }}
          />
          <Bar dataKey="count" fill="#4285f4" radius={[0, 8, 8, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default IOCStats;
