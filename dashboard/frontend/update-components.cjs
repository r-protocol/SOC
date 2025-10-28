/**
 * Script to update all React components to use static API
 * Replaces axios calls with the new api utility
 */

const fs = require('fs');
const path = require('path');

const componentsDir = path.join(__dirname, '..', '..', 'dashboard', 'frontend', 'src', 'components');

const files = [
  'PipelineOverview.jsx',
  'CategoryDistribution.jsx',
  'IOCStats.jsx',
  'RSSFeedStats.jsx',
  'ThreatFamilies.jsx',
  'ThreatTimeline.jsx',
  'TopTargetedIndustries.jsx',
  'ThreatActorActivity.jsx',
  'AttackVectorDistribution.jsx',
  'TrendingCVEs.jsx',
  'ThreatActorGeoMap.jsx',
  'ArticlePage.jsx'
];

let updated = 0;

files.forEach(filename => {
  const filePath = path.join(componentsDir, filename);
  
  if (!fs.existsSync(filePath)) {
    console.log(`⏭️  ${filename} - File not found`);
    return;
  }
  
  let content = fs.readFileSync(filePath, 'utf8');
  
  // Skip if already using api utility
  if (content.includes("from '../utils/api'") || content.includes('from "../utils/api"')) {
    console.log(`⏭️  ${filename} - Already updated`);
    return;
  }
  
  // Skip if no API_BASE
  if (!content.includes("const API_BASE = 'http://localhost:5000")) {
    console.log(`⏭️  ${filename} - No API_BASE found`);
    return;
  }
  
  console.log(`🔧 Updating ${filename}...`);
  
  // Replace imports
  content = content.replace(
    /import axios from ['"]axios['"];[\s\n]*const API_BASE = ['"]http:\/\/localhost:5000\/api['"];/,
    "import api from '../utils/api';"
  );
  
  // Replace response handling: res.data -> data
  content = content.replace(/\.then\(\s*res\s*=>/g, '.then(data =>');
  content = content.replace(/\.then\(\s*\(\s*res\s*\)\s*=>/g, '.then((data) =>');
  content = content.replace(/res\.data/g, 'data');
  
  // Replace axios.get calls with api methods
  content = content.replace(
    /axios\.get\(`\${API_BASE}\/pipeline-overview[^`]*`\)/g,
    'api.getPipelineOverview({})'
  );
  content = content.replace(
    /axios\.get\(`\${API_BASE}\/risk-distribution[^`]*`\)/g,
    'api.getRiskDistribution()'
  );
  content = content.replace(
    /axios\.get\(`\${API_BASE}\/category-distribution[^`]*`\)/g,
    'api.getCategoryDistribution({})'
  );
  content = content.replace(
    /axios\.get\(`\${API_BASE}\/threat-timeline[^`]*`\)/g,
    'api.getThreatTimeline({})'
  );
  content = content.replace(
    /axios\.get\(`\${API_BASE}\/ioc-stats[^`]*`\)/g,
    'api.getIOCStats()'
  );
  content = content.replace(
    /axios\.get\(`\${API_BASE}\/rss-feed-stats[^`]*`\)/g,
    'api.getRSSFeedStats()'
  );
  content = content.replace(
    /axios\.get\(`\${API_BASE}\/threat-families[^`]*`\)/g,
    'api.getThreatFamilies()'
  );
  content = content.replace(
    /axios\.get\(`\${API_BASE}\/top-targeted-industries[^`]*`\)/g,
    'api.getTopTargetedIndustries({})'
  );
  content = content.replace(
    /axios\.get\(`\${API_BASE}\/threat-actor-activity[^`]*`\)/g,
    'api.getThreatActorActivity({})'
  );
  content = content.replace(
    /axios\.get\(`\${API_BASE}\/attack-vectors[^`]*`\)/g,
    'api.getAttackVectors({})'
  );
  content = content.replace(
    /axios\.get\(`\${API_BASE}\/trending-cves[^`]*`\)/g,
    'api.getTrendingCVEs({})'
  );
  content = content.replace(
    /axios\.get\(`\${API_BASE}\/article\/\${([^}]+)}`\)/g,
    'api.getArticle($1)'
  );
  
  fs.writeFileSync(filePath, content, 'utf8');
  console.log(`✅ ${filename} - Updated`);
  updated++;
});

console.log(`\n✅ Updated ${updated}/${files.length} components`);
