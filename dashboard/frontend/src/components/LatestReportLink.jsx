import React, { useEffect, useState } from 'react';

/**
 * LatestReportLink
 * - Shows a button/link to download the latest published DOCX report.
 * - If reports/index.json exists, it uses the first entry for a nicer label with updated time.
 * - Falls back to reports/latest.docx.
 */
export default function LatestReportLink() {
  const base = import.meta.env.BASE_URL || '/';
  const stableUrl = `${base}reports/latest.docx`;
  const [state, setState] = useState({
    url: stableUrl,
    label: 'Download Report',
    downloadName: 'Threat_Intelligence_Report.docx'
  });

  useEffect(() => {
    const controller = new AbortController();
    const url = `${base}reports/index.json`;

    fetch(url, { signal: controller.signal })
      .then((r) => (r.ok ? r.json() : null))
      .then((list) => {
        if (Array.isArray(list) && list.length > 0) {
          const first = list[0];
          const when = first.updated ? new Date(first.updated).toLocaleString() : '';
          const rawName = first.filename || 'Threat_Intelligence_Report.docx';
          // Normalize duplicated date patterns like ..._YYYY-MM-DD_YYYY-MM-DD.docx -> ..._YYYY-MM-DD.docx
          const normalizedName = rawName.replace(/(\d{4}-\d{2}-\d{2})_(\1)(\.docx)$/i, '$1$3');
          // Always point to stable latest.docx to avoid transient 404s if dated file isn't deployed yet
          setState({
            url: stableUrl,
            // Keep the detailed info as a hover title; visible text stays "Download Report"
            label: when ? `Updated ${when}` : 'Download Report',
            downloadName: normalizedName
          });
        }
      })
      .catch(() => {
        /* ignore; fallback remains */
      });

    return () => controller.abort();
  }, [base]);

  return (
    <a
      href={state.url}
      download={state.downloadName}
      title={state.label}
      style={{
        display: 'inline-block',
        padding: '10px 16px',
        borderRadius: '8px',
        border: '2px solid #8ab4f8',
        background: '#1a1f2e',
        color: '#8ab4f8',
        textDecoration: 'none',
        fontWeight: 600,
        whiteSpace: 'nowrap'
      }}
    >
      Download Report
    </a>
  );
}
