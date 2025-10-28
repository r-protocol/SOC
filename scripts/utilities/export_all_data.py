"""
Export ALL threat_intel.db data to a single data.json file for GitHub Pages deployment
This ensures client-side filtering works for any date range.
"""

import sys
import os
import json
from pathlib import Path

# Add parent directory to path to import database module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from dashboard.backend.database import ThreatIntelDB

def export_all_data():
    """Export all articles and data without date filtering"""
    
    print("🚀 Exporting ALL data for GitHub Pages client-side filtering...")
    print("="*70)
    
    # Initialize database
    db = ThreatIntelDB()
    
    # Create output directory
    output_dir = Path(__file__).parent.parent.parent / "dashboard" / "frontend" / "public"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📁 Output directory: {output_dir}")
    print("="*70)
    
    try:
        # Get ALL recent threats without date filtering (use large number of days to get all)
        print("📊 Fetching all articles from database...", end=" ")
        all_threats = db.get_recent_threats(limit=5000, days=3650)  # 10 years = effectively all data
        print(f"✅ Found {len(all_threats)} articles")
        
        # Create the main data structure
        data = {
            "articles": all_threats,
            "metadata": {
                "total_count": len(all_threats),
                "exported_at": db.get_pipeline_overview().get('last_run'),
                "note": "Contains all articles for client-side filtering"
            }
        }
        
        # Export to data.json
        output_path = output_dir / "data.json"
        print(f"💾 Writing to {output_path}...", end=" ")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Get file size
        size_kb = output_path.stat().st_size / 1024
        size_mb = size_kb / 1024
        
        print(f"✅ Done! ({size_mb:.2f} MB)")
        
        print("="*70)
        print("✅ Export complete!")
        print(f"📁 File: {output_path}")
        print(f"📊 Articles: {len(all_threats)}")
        print(f"💾 Size: {size_mb:.2f} MB")
        print("="*70)
        print("\n🎉 Data ready for GitHub Pages deployment with client-side filtering!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    export_all_data()
