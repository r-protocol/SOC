import sqlite3
import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.analysis import analyze_article_with_llm
from src.utils.logging_utils import log_info, log_success, BColors

DB_PATH = 'threat_intel.db'

def reprocess_all_not_relevant():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Get all NOT_RELEVANT articles
    cur.execute("""
        SELECT id, title, url, content, published_date
        FROM articles
        WHERE threat_risk = 'NOT_RELEVANT'
        ORDER BY id
    """)
    
    rows = cur.fetchall()
    total = len(rows)
    
    print(f"\n{BColors.HEADER}{'='*80}{BColors.ENDC}")
    print(f"{BColors.HEADER}Reprocessing {total} NOT_RELEVANT Articles with gpt-oss:20b{BColors.ENDC}")
    print(f"{BColors.HEADER}{'='*80}{BColors.ENDC}\n")
    
    success_count = 0
    error_count = 0
    
    for i, (aid, title, url, content, published_date) in enumerate(rows, 1):
        print(f"{BColors.OKBLUE}[{i}/{total}] Reprocessing:{BColors.ENDC}")
        print(f"  ID: {aid}")
        print(f"  Title: {title[:80]}...")
        
        # Create article dict for analysis
        article = {
            'title': title,
            'url': url,
            'content': content,
            'published_date': published_date
        }
        
        # Reanalyze the article
        try:
            result, _ = analyze_article_with_llm(article)
            
            if result:
                # Convert recommendations to JSON string if it's a list
                recommendations_str = json.dumps(result.get('recommendations', [])) if isinstance(result.get('recommendations'), list) else result.get('recommendations', '')
                
                # Update the database
                cur.execute("""
                    UPDATE articles
                    SET threat_risk = ?,
                        category = ?,
                        summary = ?,
                        recommendations = ?
                    WHERE id = ?
                """, (
                    result['threat_risk'],
                    result['category'],
                    result['summary'],
                    recommendations_str,
                    aid
                ))
                conn.commit()
                
                # Show if classification changed
                if result['threat_risk'] != 'NOT_RELEVANT':
                    print(f"  {BColors.OKGREEN}✓ RECLASSIFIED: {result['threat_risk']} | {result['category']}{BColors.ENDC}\n")
                else:
                    print(f"  {BColors.WARNING}○ Still NOT_RELEVANT | {result['category']}{BColors.ENDC}\n")
                
                success_count += 1
            else:
                print(f"  {BColors.WARNING}⚠ Analysis returned no result{BColors.ENDC}\n")
                error_count += 1
        
        except Exception as e:
            print(f"  {BColors.FAIL}✗ Error: {str(e)}{BColors.ENDC}\n")
            error_count += 1
            continue
    
    conn.close()
    
    print(f"\n{BColors.OKGREEN}{'='*80}{BColors.ENDC}")
    print(f"{BColors.OKGREEN}Reprocessing Complete{BColors.ENDC}")
    print(f"{BColors.OKGREEN}Successfully processed: {success_count}/{total}{BColors.ENDC}")
    if error_count > 0:
        print(f"{BColors.WARNING}Errors: {error_count}{BColors.ENDC}")
    print(f"{BColors.OKGREEN}{'='*80}{BColors.ENDC}\n")
    
    log_success(f"Successfully reprocessed {success_count} articles")

if __name__ == '__main__':
    reprocess_all_not_relevant()
