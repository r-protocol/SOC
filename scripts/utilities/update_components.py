"""
Script to update all React components to use the new API utility
"""

import os
import re
from pathlib import Path

def update_component(file_path):
    """Update a single component file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Skip if already using the api utility
    if "from '../utils/api'" in content or 'from "../utils/api"' in content:
        print(f"⏭️  {file_path.name} - Already updated")
        return False
    
    # Skip if no API_BASE definition found
    if "const API_BASE = 'http://localhost:5000" not in content:
        print(f"⏭️  {file_path.name} - No API_BASE found")
        return False
    
    print(f"🔧 Updating {file_path.name}...")
    
    # Replace imports
    content = re.sub(
        r"import axios from 'axios';\s*\nconst API_BASE = 'http://localhost:5000/api';",
        "import api from '../utils/api';",
        content
    )
    
    # Replace axios.get calls with api methods
    replacements = {
        r"axios\.get\(`\${API_BASE}/pipeline-overview([^`]*)`\)": "api.getPipelineOverview({})",
        r"axios\.get\(`\${API_BASE}/risk-distribution([^`]*)`\)": "api.getRiskDistribution()",
        r"axios\.get\(`\${API_BASE}/category-distribution([^`]*)`\)": "api.getCategoryDistribution({})",
        r"axios\.get\(`\${API_BASE}/threat-timeline([^`]*)`\)": "api.getThreatTimeline({})",
        r"axios\.get\(`\${API_BASE}/recent-threats([^`]*)`\)": "api.getRecentThreats({})",
        r"axios\.get\(`\${API_BASE}/ioc-stats([^`]*)`\)": "api.getIOCStats()",
        r"axios\.get\(`\${API_BASE}/rss-feed-stats([^`]*)`\)": "api.getRSSFeedStats()",
        r"axios\.get\(`\${API_BASE}/threat-families([^`]*)`\)": "api.getThreatFamilies()",
        r"axios\.get\(`\${API_BASE}/top-targeted-industries([^`]*)`\)": "api.getTopTargetedIndustries({})",
        r"axios\.get\(`\${API_BASE}/threat-actor-activity([^`]*)`\)": "api.getThreatActorActivity({})",
        r"axios\.get\(`\${API_BASE}/attack-vectors([^`]*)`\)": "api.getAttackVectors({})",
        r"axios\.get\(`\${API_BASE}/trending-cves([^`]*)`\)": "api.getTrendingCVEs({})",
        r"axios\.get\(`\${API_BASE}/article/\${([^}]+)}`\)": r"api.getArticle(\1)",
    }
    
    for pattern, replacement in replacements.items():
        content = re.sub(pattern, replacement, content)
    
    # Handle .then(res => with .then(data =>
    content = content.replace('.then(res => ', '.then(data => ')
    content = content.replace('.then((res) => ', '.then((data) => ')
    content = content.replace('res.data', 'data')
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ {file_path.name} - Updated successfully")
        return True
    else:
        print(f"⏭️  {file_path.name} - No changes needed")
        return False

def main():
    """Update all components"""
    components_dir = Path(__file__).parent.parent.parent / "dashboard" / "frontend" / "src" / "components"
    
    print("🚀 Updating React components to use new API utility")
    print("="*70)
    
    if not components_dir.exists():
        print(f"❌ Components directory not found: {components_dir}")
        return
    
    jsx_files = list(components_dir.glob("*.jsx"))
    updated_count = 0
    
    for file_path in jsx_files:
        if update_component(file_path):
            updated_count += 1
    
    print("="*70)
    print(f"✅ Updated {updated_count}/{len(jsx_files)} components")

if __name__ == "__main__":
    main()
