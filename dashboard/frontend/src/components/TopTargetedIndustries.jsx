import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

const API_BASE = 'http://localhost:5000/api';

const COLORS = ['#ea4335', '#ff6d01', '#fbbc04', '#34a853', '#4285f4', '#a142f4', '#f538a0', '#00d9c0'];

function TopTargetedIndustries({ timeRange }) {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Build time range parameters
    let timeParams = '';
    if (timeRange.type === 'daterange' && timeRange.startDate && timeRange.endDate) {
      timeParams = `?start_date=${timeRange.startDate}&end_date=${timeRange.endDate}`;
    } else if (timeRange.days) {
      timeParams = `?days=${timeRange.days}`;
    }
    
    api.getTopTargetedIndustries({})
      .then(data => {
        setData(data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, [timeRange]);

  if (loading) return <div className="card loading">Loading industries...</div>;

  return (
    <div className="card">
      <div className="card-title">🏢 Top Targeted Industries</div>
      {data.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '40px', color: '#a1a1aa' }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>📊</div>
          <div>No industry data available</div>
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={Math.max(300, data.length * 40)}>
          <BarChart data={data} layout="vertical" margin={{ left: 120, right: 20, top: 10, bottom: 10 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#3a3a4a" />
            <XAxis type="number" stroke="#a1a1aa" />
            <YAxis 
              type="category" 
              dataKey="name" 
              stroke="#a1a1aa"
              width={110}
              tick={{ fontSize: 13 }}
            />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#2a2a3e', 
                border: '1px solid #3f3f55',
                borderRadius: '6px'
              }}
              cursor={{ fill: '#3a3a4a' }}
            />
            <Bar dataKey="value" radius={[0, 8, 8, 0]}>
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}

export default TopTargetedIndustries;
