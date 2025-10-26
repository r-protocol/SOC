"""
Test the improved filtering logic on recent articles
"""
import sqlite3
import sys
import os
# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.filtering import is_article_relevant_with_llm

def test_improved_filtering():
    conn = sqlite3.connect('threat_intel.db')
    cursor = conn.cursor()
    
    # Get recent articles marked as NOT_RELEVANT
    cursor.execute('''
        SELECT id, title, content, threat_risk, category 
        FROM articles 
        WHERE threat_risk = 'NOT_RELEVANT'
        ORDER BY published_date DESC 
        LIMIT 15
    ''')
    
    articles = cursor.fetchall()
    conn.close()
    
    print(f"🧪 Testing improved filter on {len(articles)} articles marked NOT_RELEVANT\n")
    print("="*80)
    
    changed = 0
    correct = 0
    
    for article_id, title, content, risk, category in articles:
        article_dict = {'title': title, 'content': content}
        new_result = is_article_relevant_with_llm(article_dict)
        
        print(f"\nTitle: {title[:70]}")
        print(f"Old: NOT_RELEVANT | New: {'RELEVANT' if new_result else 'NOT_RELEVANT'}")
        
        if new_result:
            changed += 1
            print("✅ NOW DETECTED AS RELEVANT (was incorrectly filtered)")
        else:
            correct += 1
            print("✓ Correctly marked as NOT_RELEVANT")
    
    print("\n" + "="*80)
    print(f"\n📊 Results:")
    print(f"  Changed to RELEVANT: {changed}/{len(articles)} ({changed/len(articles)*100:.1f}%)")
    print(f"  Still NOT_RELEVANT: {correct}/{len(articles)} ({correct/len(articles)*100:.1f}%)")
    
    if changed > 0:
        print(f"\n✨ Improvement: {changed} previously missed articles would now be caught!")
    
if __name__ == "__main__":
    test_improved_filtering()
