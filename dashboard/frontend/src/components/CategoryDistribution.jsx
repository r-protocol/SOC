import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const API_BASE = 'http://localhost:5000/api';

const COLORS = ['#ea4335', '#ff6d01', '#fbbc04', '#34a853', '#4285f4', '#a142f4', '#f538a0', '#00d9c0'];

function CategoryDistribution({ timeRange }) {
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
    
    api.getCategoryDistribution({})
      .then(data => {
        // Exclude placeholder category from the pie chart
        const filtered = Array.isArray(data)
          ? data.filter(item => item?.name !== 'Pending Analysis')
          : [];
        setData(filtered);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, [timeRange]);

  if (loading) return <div className="card loading">Loading categories...</div>;

  return (
    <div className="card">
      <div className="card-title">🍩 Category Distribution</div>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
            outerRadius={100}
            fill="#8884d8"
            dataKey="value"
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip 
            contentStyle={{ backgroundColor: '#2a2a3e', border: '1px solid #3f3f55' }}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}

export default CategoryDistribution;
