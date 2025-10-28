import React, { useState, useEffect } from 'react';
import api from '../utils/api';
import { aggregateTimelineData } from '../utils/filters';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

function ThreatTimeline({ timeRange }) {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [allThreats, setAllThreats] = useState([]);

  // Load all threats once for production mode
  useEffect(() => {
    if (import.meta.env.PROD) {
      api.getRecentThreats({})
        .then(threats => {
          setAllThreats(threats);
          setLoading(false);
        })
        .catch(err => {
          console.error(err);
          setLoading(false);
        });
    }
  }, []);

  // Filter and aggregate when timeRange changes (production)
  useEffect(() => {
    if (import.meta.env.PROD && allThreats.length > 0) {
      const aggregated = aggregateTimelineData(allThreats, timeRange);
      setData(aggregated);
    }
  }, [timeRange, allThreats]);

  // For development mode, fetch from API with parameters
  useEffect(() => {
    if (!import.meta.env.PROD) {
      const options = {};
      if (timeRange.type === 'daterange' && timeRange.startDate && timeRange.endDate) {
        options.start_date = timeRange.startDate;
        options.end_date = timeRange.endDate;
      } else if (timeRange.days) {
        options.days = timeRange.days;
      }
      
      api.getThreatTimeline(options)
        .then(data => {
          setData(data);
        })
        .catch(err => {
          console.error(err);
        });
    }
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
