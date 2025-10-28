/**
 * API utility that works for both static JSON (GitHub Pages) and live backend API
 * 
 * In production (GitHub Pages), it reads from /data/*.json files
 * In development, it can use the live backend API at localhost:5000
 */

const IS_PRODUCTION = import.meta.env.PROD;
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';
// Use Vite base to construct the correct path both locally (preview) and on GitHub Pages
const STATIC_DATA_BASE = `${import.meta.env.BASE_URL}data`;

/**
 * Fetch data from either static JSON or API endpoint
 */
async function fetchData(endpoint, options = {}) {
  try {
    // In production (GitHub Pages), use static JSON files
    if (IS_PRODUCTION) {
      const staticUrl = `${STATIC_DATA_BASE}/${endpoint}.json`;
      console.log(`📡 Fetching static data: ${staticUrl}`);
      const response = await fetch(staticUrl);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch ${staticUrl}: ${response.statusText}`);
      }
      
      return await response.json();
    }
    
    // In development, use live API
    const apiUrl = `${API_BASE_URL}/${endpoint}`;
    console.log(`📡 Fetching from API: ${apiUrl}`);
    
    const queryParams = new URLSearchParams(options).toString();
    const fullUrl = queryParams ? `${apiUrl}?${queryParams}` : apiUrl;
    
    const response = await fetch(fullUrl);
    
    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`Error fetching ${endpoint}:`, error);
    throw error;
  }
}

/**
 * Fetch article details by ID
 * In production, reads from /data/articles/{id}.json
 * In development, calls API endpoint
 */
async function fetchArticle(articleId) {
  try {
    if (IS_PRODUCTION) {
      const staticUrl = `${STATIC_DATA_BASE}/articles/${articleId}.json`;
      console.log(`📡 Fetching static article: ${staticUrl}`);
      const response = await fetch(staticUrl);
      
      if (!response.ok) {
        throw new Error(`Article ${articleId} not found`);
      }
      
      return await response.json();
    }
    
    // In development, use live API
    const apiUrl = `${API_BASE_URL}/article/${articleId}`;
    console.log(`📡 Fetching article from API: ${apiUrl}`);
    
    const response = await fetch(apiUrl);
    
    if (!response.ok) {
      throw new Error(`Article ${articleId} not found`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`Error fetching article ${articleId}:`, error);
    throw error;
  }
}

// Export API functions as default export
const api = {
  // Dashboard data endpoints
  getPipelineOverview: (options) => fetchData('pipeline-overview', options),
  getRiskDistribution: () => fetchData('risk-distribution'),
  getCategoryDistribution: (options) => fetchData('category-distribution', options),
  getThreatTimeline: (options) => fetchData('threat-timeline', options),
  getRecentThreats: (options) => fetchData('recent-threats', options),
  getIOCStats: () => fetchData('ioc-stats'),
  getRSSFeedStats: () => fetchData('rss-feed-stats'),
  getThreatFamilies: () => fetchData('threat-families'),
  getTopTargetedIndustries: (options) => fetchData('top-targeted-industries', options),
  getThreatActorActivity: (options) => fetchData('threat-actor-activity', options),
  getAttackVectors: (options) => fetchData('attack-vectors', options),
  getTrendingCVEs: (options) => fetchData('trending-cves', options),
  
  // Article details
  getArticle: fetchArticle,
};

export default api;
