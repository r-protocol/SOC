import React, { useState, useEffect } from 'react';
import api from '../utils/api';
import { filterByTimeRange } from '../utils/filters';

function PipelineOverview({ timeRange }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [allThreats, setAllThreats] = useState([]);
  const [totals, setTotals] = useState(null); // Holds overall totals from pipeline-overview in prod

  // Load all data once for production mode
  useEffect(() => {
    if (import.meta.env.PROD) {
      // In production (static hosting), load both recent threats (for filtering)
      // and pipeline overview (for stable totals) to mirror backend semantics
      Promise.all([
        api.getRecentThreats({}),
        api.getPipelineOverview({})
      ])
        .then(([threats, overview]) => {
          setAllThreats(threats || []);
          setTotals(overview || null);
          setLoading(false);
        })
        .catch(err => {
          console.error(err);
          setLoading(false);
        });
    } else {
      // Development mode - use backend API
      const options = {};
      if (timeRange.type === 'daterange' && timeRange.startDate && timeRange.endDate) {
        options.start_date = timeRange.startDate;
        options.end_date = timeRange.endDate;
      } else if (timeRange.days) {
        options.days = timeRange.days;
      }
      
      api.getPipelineOverview(options)
        .then(data => {
          setData(data);
          setLoading(false);
        })
        .catch(err => {
          console.error(err);
          setLoading(false);
        });
    }
  }, []);

  // Calculate stats based on filtered data for production
  useEffect(() => {
    if (import.meta.env.PROD && allThreats.length > 0) {
      const filtered = filterByTimeRange(allThreats, timeRange);
      
      // Use totals from pipeline-overview when available to match backend behavior
      const stats = {
        critical_threats: filtered.filter(t => t.risk_level === 'HIGH').length,
        articles_processed: totals?.articles_processed ?? allThreats.length,
        total_iocs: totals?.total_iocs ?? filtered.reduce((sum, t) => sum + (t.ioc_count || 0), 0),
        total_kql: totals?.total_kql ?? filtered.reduce((sum, t) => sum + (t.kql_count || 0), 0),
        filtered_items: filtered.length
      };
      
      setData(stats);
    }
  }, [timeRange, allThreats, totals]);

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
      <div className="card kpi-card info">
        <div className="kpi-label">KQL Generated</div>
        <div className="kpi-value">{data.total_kql}</div>
      </div>
      <div className="card kpi-card warning">
        <div className="kpi-label">Recent ({timeRange.days ? `${timeRange.days} days` : 'filtered'})</div>
        <div className="kpi-value">{data.filtered_items}</div>
      </div>
    </>
  );
}

export default PipelineOverview;
