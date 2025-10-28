import React, { useState, useEffect } from 'react';
import api from '../utils/api';
import { aggregateAttackVectors } from '../utils/filters';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const COLORS = ['#ea4335', '#ff6d01', '#fbbc04', '#34a853', '#4285f4', '#a142f4', '#f538a0', '#00d9c0'];

function AttackVectorDistribution({ timeRange }) {
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
      const aggregated = aggregateAttackVectors(allThreats, timeRange);
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
      
      api.getAttackVectors(options)
        .then(data => {
          setData(data);
          setLoading(false);
        })
        .catch(err => {
          console.error(err);
          setLoading(false);
        });
    }
  }, [timeRange]);

  if (loading) return <div className="card loading">Loading attack vectors...</div>;

  const CustomLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent }) => {
    const RADIAN = Math.PI / 180;
    const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
    const x = cx + radius * Math.cos(-midAngle * RADIAN);
    const y = cy + radius * Math.sin(-midAngle * RADIAN);

    if (percent < 0.05) return null; // Hide labels for small slices

    return (
      <text 
        x={x} 
        y={y} 
        fill="white" 
        textAnchor={x > cx ? 'start' : 'end'} 
        dominantBaseline="central"
        style={{ fontSize: '12px', fontWeight: '600' }}
      >
        {`${(percent * 100).toFixed(0)}%`}
      </text>
    );
  };

  return (
    <div className="card">
      <div className="card-title">🎯 Attack Vector Distribution</div>
      {data.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '40px', color: '#a1a1aa' }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>📊</div>
          <div>No attack vector data available</div>
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={320}>
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={CustomLabel}
              outerRadius={110}
              fill="#8884d8"
              dataKey="value"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#2a2a3e', 
                border: '1px solid #3f3f55',
                borderRadius: '6px'
              }}
            />
            <Legend 
              verticalAlign="bottom" 
              height={36}
              wrapperStyle={{ fontSize: '12px' }}
            />
          </PieChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}

export default AttackVectorDistribution;
