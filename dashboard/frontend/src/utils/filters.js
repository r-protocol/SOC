/**
 * Client-side filtering utilities for static deployment
 * These functions filter pre-loaded data based on time ranges and other criteria
 */

/**
 * Filter threats by date range
 */
export function filterByTimeRange(items, timeRange, dateField = 'published_date') {
  if (!timeRange) return items;
  
  let filtered = items;
  
  if (timeRange.type === 'daterange' && timeRange.startDate && timeRange.endDate) {
    const start = new Date(timeRange.startDate).getTime();
    const end = new Date(timeRange.endDate).getTime();
    filtered = filtered.filter(item => {
      const itemDate = new Date(item[dateField]).getTime();
      return itemDate >= start && itemDate <= end;
    });
  } else if (timeRange.days) {
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - timeRange.days);
    filtered = filtered.filter(item => {
      const itemDate = new Date(item[dateField]);
      return itemDate >= cutoffDate;
    });
  }
  
  return filtered;
}

/**
 * Aggregate timeline data by date
 */
export function aggregateTimelineData(threats, timeRange) {
  // Filter by time range first
  const filtered = filterByTimeRange(threats, timeRange);
  
  // Group by date and risk level
  const grouped = {};
  
  filtered.forEach(threat => {
    const date = new Date(threat.published_date).toISOString().split('T')[0];
    
    if (!grouped[date]) {
      grouped[date] = { date, HIGH: 0, MEDIUM: 0, LOW: 0, INFORMATIONAL: 0 };
    }
    
    const risk = threat.risk_level || 'INFORMATIONAL';
    grouped[date][risk] = (grouped[date][risk] || 0) + 1;
  });
  
  // Convert to array and sort by date
  return Object.values(grouped).sort((a, b) => new Date(a.date) - new Date(b.date));
}

/**
 * Aggregate category distribution
 */
export function aggregateCategoryDistribution(threats, timeRange) {
  const filtered = filterByTimeRange(threats, timeRange);
  
  const categoryCount = {};
  filtered.forEach(threat => {
    const category = threat.category || 'Uncategorized';
    categoryCount[category] = (categoryCount[category] || 0) + 1;
  });
  
  return Object.entries(categoryCount)
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value);
}

/**
 * Aggregate attack vector distribution
 */
export function aggregateAttackVectors(threats, timeRange) {
  const filtered = filterByTimeRange(threats, timeRange);
  
  const vectorCount = {};
  filtered.forEach(threat => {
    // Extract attack vectors from category or other fields
    const category = threat.category || 'Unknown';
    
    // Map categories to attack vectors
    let vector = 'Other';
    if (category.includes('Phishing') || category.includes('Email')) {
      vector = 'Phishing/Email';
    } else if (category.includes('Malware') || category.includes('Ransomware')) {
      vector = 'Malware';
    } else if (category.includes('Vulnerability') || category.includes('Exploit')) {
      vector = 'Exploitation';
    } else if (category.includes('Credential')) {
      vector = 'Credential Theft';
    } else if (category.includes('Web') || category.includes('Application')) {
      vector = 'Web Application';
    } else if (category.includes('Network')) {
      vector = 'Network';
    }
    
    vectorCount[vector] = (vectorCount[vector] || 0) + 1;
  });
  
  return Object.entries(vectorCount)
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value);
}

/**
 * Aggregate top targeted industries
 * Extracts industries from article content using keyword matching
 */
export function aggregateTopIndustries(threats, timeRange) {
  const filtered = filterByTimeRange(threats, timeRange);
  
  const industryCount = {};
  
  // Industry keywords mapping (matching backend logic)
  const industryKeywords = {
    'Finance': ['bank', 'financial', 'finance', 'payment', 'credit', 'trading', 'fintech', 'cryptocurrency', 'crypto'],
    'Healthcare': ['health', 'hospital', 'medical', 'patient', 'healthcare', 'pharmaceutical', 'clinic'],
    'Government': ['government', 'federal', 'state', 'military', 'defense', 'agency', 'public sector'],
    'Manufacturing': ['manufacturing', 'industrial', 'factory', 'production', 'automotive', 'supply chain'],
    'Technology': ['tech', 'software', 'cloud', 'saas', 'it company', 'technology firm'],
    'Energy': ['energy', 'oil', 'gas', 'utility', 'power', 'electric', 'renewable'],
    'Retail': ['retail', 'ecommerce', 'e-commerce', 'shopping', 'store', 'consumer'],
    'Education': ['education', 'university', 'school', 'college', 'academic', 'student'],
    'Telecommunications': ['telecom', 'telecommunications', 'mobile', 'network provider', 'isp'],
    'Transportation': ['transportation', 'airline', 'shipping', 'logistics', 'aviation']
  };
  
  filtered.forEach(threat => {
    // Combine all text fields for keyword matching
    const text = [
      threat.category || '',
      threat.title || '',
      threat.summary || '',
      threat.content || ''
    ].join(' ').toLowerCase();
    
    // Check each industry's keywords
    for (const [industry, keywords] of Object.entries(industryKeywords)) {
      if (keywords.some(keyword => text.includes(keyword))) {
        industryCount[industry] = (industryCount[industry] || 0) + 1;
      }
    }
  });
  
  // Sort by count and return top 15 with correct property names
  return Object.entries(industryCount)
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value)
    .slice(0, 15);
}
