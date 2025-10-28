"""
Export SQLite database to JSON for static GitHub Pages hosting
This creates a data.json file that the frontend can fetch directly
"""

import sqlite3
import json
from datetime import datetime

DB_PATH = 'threat_intel.db'
OUTPUT_PATH = 'dashboard/frontend/public/data.json'

def export_database_to_json():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    cur = conn.cursor()
    
    data = {}
    
    # Export articles
    print("Exporting articles...")
    cur.execute("""
        SELECT id, title, url, published_date, content, summary, 
               threat_risk, category, recommendations
        FROM articles
        ORDER BY published_date DESC
    """)
    articles = [dict(row) for row in cur.fetchall()]
    data['articles'] = articles
    print(f"  ✓ Exported {len(articles)} articles")
    
    # Export stats
    print("Calculating statistics...")
    
    # Risk distribution
    cur.execute("""
        SELECT threat_risk, COUNT(*) as count
        FROM articles
        GROUP BY threat_risk
    """)
    data['risk_distribution'] = [dict(row) for row in cur.fetchall()]
    
    # Category distribution
    cur.execute("""
        SELECT category, COUNT(*) as count
        FROM articles
        GROUP BY category
        ORDER BY count DESC
    """)
    data['category_distribution'] = [dict(row) for row in cur.fetchall()]
    
    # Total counts
    cur.execute("SELECT COUNT(*) as total FROM articles")
    data['total_articles'] = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) as high FROM articles WHERE threat_risk = 'HIGH'")
    data['high_risk_count'] = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) as medium FROM articles WHERE threat_risk = 'MEDIUM'")
    data['medium_risk_count'] = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) as low FROM articles WHERE threat_risk = 'LOW'")
    data['low_risk_count'] = cur.fetchone()[0]
    
    # Recent articles by date
    cur.execute("""
        SELECT DATE(published_date) as date, COUNT(*) as count, threat_risk
        FROM articles
        WHERE published_date >= date('now', '-30 days')
        GROUP BY DATE(published_date), threat_risk
        ORDER BY date DESC
    """)
    data['timeline'] = [dict(row) for row in cur.fetchall()]
    
    # Export metadata
    data['exported_at'] = datetime.now().isoformat()
    data['version'] = '1.0'
    
    # Write to JSON file
    print(f"\nWriting to {OUTPUT_PATH}...")
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    conn.close()
    
    print(f"\n✅ Successfully exported database to {OUTPUT_PATH}")
    print(f"   Total articles: {data['total_articles']}")
    print(f"   HIGH risk: {data['high_risk_count']}")
    print(f"   MEDIUM risk: {data['medium_risk_count']}")
    print(f"   LOW risk: {data['low_risk_count']}")
    print(f"   File size: {len(json.dumps(data)) / 1024:.2f} KB")

if __name__ == '__main__':
    export_database_to_json()
