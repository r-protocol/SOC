import sqlite3
import sys
import os
# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.analysis import analyze_article_with_llm

# Test with the Pwn2Own article that was incorrectly marked as HIGH
conn = sqlite3.connect('threat_intel.db')
cursor = conn.cursor()

# Get the Pwn2Own article
cursor.execute('''SELECT title, content, url, published_date 
                  FROM articles 
                  WHERE title LIKE "%Pwn2Own%"
                  LIMIT 1''')

result = cursor.fetchone()
if result:
    test_article = {
        'title': result[0],
        'content': result[1],
        'url': result[2],
        'published_date': result[3]
    }
    
    print(f"\n{'='*80}")
    print(f"Testing article: {test_article['title']}")
    print(f"{'='*80}\n")
    
    analysis, _ = analyze_article_with_llm(test_article)
    
    if analysis:
        print(f"✓ Analysis successful!")
        print(f"\nThreat Risk: {analysis.get('threat_risk')}")
        print(f"Category: {analysis.get('category')}")
        print(f"\nSummary: {analysis.get('summary')[:300]}...")
    else:
        print("✗ Analysis failed")
else:
    print("No Pwn2Own article found")

# Also test with a newsletter article
print(f"\n\n{'='*80}")
cursor.execute('''SELECT title, content, url, published_date 
                  FROM articles 
                  WHERE title LIKE "%newsletter%"
                  LIMIT 1''')

result = cursor.fetchone()
if result:
    test_article = {
        'title': result[0],
        'content': result[1],
        'url': result[2],
        'published_date': result[3]
    }
    
    print(f"Testing article: {test_article['title']}")
    print(f"{'='*80}\n")
    
    analysis, _ = analyze_article_with_llm(test_article)
    
    if analysis:
        print(f"✓ Analysis successful!")
        print(f"\nThreat Risk: {analysis.get('threat_risk')}")
        print(f"Category: {analysis.get('category')}")
        print(f"\nSummary: {analysis.get('summary')[:300]}...")
    else:
        print("✗ Analysis failed")

conn.close()
