import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = 'http://localhost:5000/api';

function PipelineOverview({ timeRange }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Build time range parameters
    let timeParams = '';
    if (timeRange.type === 'daterange' && timeRange.startDate && timeRange.endDate) {
      timeParams = `?start_date=${timeRange.startDate}&end_date=${timeRange.endDate}`;
    } else if (timeRange.days) {
      timeParams = `?days=${timeRange.days}`;
    }
    
    axios.get(`${API_BASE}/pipeline-overview${timeParams}`)
      .then(res => {
        setData(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, [timeRange]);

  if (loading) return <div className="card loading">Loading...</div>;
  if (!data) return null;

  return (
    <>
      <div className="card kpi-card critical">
        <div className="kpi-label">Critical Threats</div>
        <div className="kpi-value">{data.critical_threats}</div>
      </div>
      <div className="card kpi-card">
        <div className="kpi-label">Articles Processed</div>
        <div className="kpi-value">{data.articles_processed}</div>
      </div>
      <div className="card kpi-card success">
        <div className="kpi-label">IOCs Extracted</div>
        <div className="kpi-value">{data.total_iocs}</div>
      </div>
      <div className="card kpi-card warning">
        <div className="kpi-label">Recent (7 days)</div>
        <div className="kpi-value">{data.filtered_items}</div>
      </div>
    </>
  );
}

export default PipelineOverview;
