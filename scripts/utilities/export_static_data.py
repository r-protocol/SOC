"""
Export threat_intel.db data to static JSON files for GitHub Pages deployment
This script generates JSON files that the frontend can consume without needing a backend API.
"""

import sys
import os
import json
from pathlib import Path

# Add parent directory to path to import database module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from dashboard.backend.database import ThreatIntelDB

def export_to_json():
    """Export all dashboard data to static JSON files"""
    
    print("🚀 Starting static data export for GitHub Pages...")
    print("="*70)
    
    # Initialize database
    db = ThreatIntelDB()
    
    # Create output directory
    output_dir = Path(__file__).parent.parent.parent / "dashboard" / "frontend" / "public" / "data"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📁 Output directory: {output_dir}")
    print("="*70)
    
    # Export functions mapping
    # Expand export window to cover last 4-12 months for richer client-side filtering
    EXPORT_DAYS = 365  # include up to 1 year to capture all 333+ items
    exports = {
        'pipeline-overview.json': lambda: db.get_pipeline_overview(days=EXPORT_DAYS),
        'risk-distribution.json': lambda: db.get_risk_distribution(),
        'category-distribution.json': lambda: db.get_category_distribution(days=EXPORT_DAYS),
        'threat-timeline.json': lambda: db.get_threat_timeline(days=EXPORT_DAYS),
        'recent-threats.json': lambda: db.get_recent_threats(limit=5000, days=EXPORT_DAYS),
        'ioc-stats.json': lambda: db.get_ioc_stats(),
        'rss-feed-stats.json': lambda: db.get_rss_feed_stats(),
        'threat-families.json': lambda: db.get_threat_families(),
        'top-targeted-industries.json': lambda: db.get_top_targeted_industries(limit=50, days=EXPORT_DAYS),
        'threat-actor-activity.json': lambda: db.get_threat_actor_activity(limit=200, days=EXPORT_DAYS),
        'attack-vectors.json': lambda: db.get_attack_vectors(days=EXPORT_DAYS),
        'trending-cves.json': lambda: db.get_trending_cves(limit=100, days=EXPORT_DAYS),
    }
    
    # Export each dataset
    success_count = 0
    for filename, export_func in exports.items():
        try:
            print(f"📊 Exporting {filename}...", end=" ")
            data = export_func()
            
            output_path = output_dir / filename
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Get file size
            size_kb = output_path.stat().st_size / 1024
            
            # Count items
            if isinstance(data, list):
                count = len(data)
                print(f"✅ {count} items ({size_kb:.1f} KB)")
            elif isinstance(data, dict):
                count = len(data)
                print(f"✅ {count} keys ({size_kb:.1f} KB)")
            else:
                print(f"✅ ({size_kb:.1f} KB)")
            
            success_count += 1
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("="*70)
    
    # Export individual article details (for the article detail page)
    print("📖 Exporting individual article details...")
    
    # Get all article IDs from recent threats
    try:
        recent_threats = db.get_recent_threats(limit=1000, days=365)  # Last year of data
        article_ids = [threat['id'] for threat in recent_threats]
        
        articles_dir = output_dir / "articles"
        articles_dir.mkdir(exist_ok=True)
        
        article_count = 0
        for article_id in article_ids:
            try:
                article_data = db.get_article_details(article_id)
                if article_data:
                    article_path = articles_dir / f"{article_id}.json"
                    with open(article_path, 'w', encoding='utf-8') as f:
                        json.dump(article_data, f, indent=2, ensure_ascii=False)
                    article_count += 1
            except Exception as e:
                print(f"⚠️  Error exporting article {article_id}: {e}")
        
        print(f"✅ Exported {article_count} individual articles")
        success_count += 1
        
    except Exception as e:
        print(f"❌ Error exporting articles: {e}")
    
    print("="*70)
    print(f"✅ Export complete! {success_count}/{len(exports) + 1} datasets exported")
    print(f"📁 Files saved to: {output_dir}")
    print("="*70)
    
    # Create a manifest file with metadata
    manifest = {
        "generated_at": db.get_pipeline_overview().get('last_run'),
        "total_articles": db.get_pipeline_overview().get('articles_processed', 0),
        "endpoints": list(exports.keys()),
        "article_count": article_count if 'article_count' in locals() else 0
    }
    
    manifest_path = output_dir / "manifest.json"
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"📋 Manifest created: {manifest_path}")
    print("\n🎉 Static data export complete! Ready for GitHub Pages deployment.")

if __name__ == "__main__":
    export_to_json()
