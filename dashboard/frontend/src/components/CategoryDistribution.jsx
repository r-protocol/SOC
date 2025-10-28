import React, { useState, useEffect } from 'react';
import api from '../utils/api';
import { aggregateCategoryDistribution } from '../utils/filters';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const COLORS = ['#ea4335', '#ff6d01', '#fbbc04', '#34a853', '#4285f4', '#a142f4', '#f538a0', '#00d9c0'];

function CategoryDistribution({ timeRange }) {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [allThreats, setAllThreats] = useState([]);

  // Load all threats once
  useEffect(() => {
    api.getRecentThreats({})
      .then(threats => {
        setAllThreats(threats);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  // Filter and aggregate when timeRange changes
  useEffect(() => {
    if (import.meta.env.PROD && allThreats.length > 0) {
      const aggregated = aggregateCategoryDistribution(allThreats, timeRange);
      const filtered = aggregated.filter(item => item?.name !== 'Pending Analysis');
      setData(filtered);
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
      
      api.getCategoryDistribution(options)
        .then(data => {
          const filtered = Array.isArray(data)
            ? data.filter(item => item?.name !== 'Pending Analysis')
            : [];
          setData(filtered);
        })
        .catch(err => {
          console.error(err);
        });
    }
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
