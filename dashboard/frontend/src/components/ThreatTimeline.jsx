import React, { useState, useEffect } from 'react';
import api from '../utils/api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

function ThreatTimeline({ timeRange }) {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Build time range parameters
    let timeParams = '';
    if (timeRange.type === 'daterange' && timeRange.startDate && timeRange.endDate) {
      timeParams = `start_date=${timeRange.startDate}&end_date=${timeRange.endDate}`;
    } else if (timeRange.days) {
      timeParams = `days=${timeRange.days}`;
    }
    
    api.getThreatTimeline({})
      .then(data => {
        setData(data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, [timeRange]);

  if (loading) return <div className="card loading">Loading timeline...</div>;

  const displayDays = timeRange.days || 7;
  const displayLabel = timeRange.type === 'daterange' && timeRange.startDate && timeRange.endDate
    ? `${new Date(timeRange.startDate).toLocaleDateString()} - ${new Date(timeRange.endDate).toLocaleDateString()}`
    : `${displayDays} Days`;

  return (
    <div className="card">
      <div className="card-title">📈 Threat Timeline ({displayLabel})</div>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#3f3f55" />
          <XAxis dataKey="date" stroke="#a1a1aa" />
          <YAxis stroke="#a1a1aa" />
          <Tooltip 
            contentStyle={{ backgroundColor: '#2a2a3e', border: '1px solid #3f3f55' }}
            labelStyle={{ color: '#e4e4e7' }}
          />
          <Legend />
          <Line type="monotone" dataKey="HIGH" stroke="#ea4335" strokeWidth={2} />
          <Line type="monotone" dataKey="MEDIUM" stroke="#fbbc04" strokeWidth={2} />
          <Line type="monotone" dataKey="LOW" stroke="#34a853" strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default ThreatTimeline;
