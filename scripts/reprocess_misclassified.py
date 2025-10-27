import sqlite3
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.analysis import analyze_article_with_llm
from src.utils.logging_utils import log_info, log_success, BColors

DB_PATH = 'threat_intel.db'

# Article IDs that are clearly cybersecurity-related but misclassified
MISCLASSIFIED_IDS = [
    210,  # NTLM LDAP Authentication Bypass Vulnerability (CVE-2025-54918)
    213,  # CrowdStrike 2025 APJ eCrime Landscape Report
    215,  # Git Vulnerability CVE-2025-48384
    218,  # Living-off-the-Land Attacks
    219,  # October 2025 Patch Tuesday
    221,  # Intelligence Insights: October 2025
    222,  # Adversaries abusing AI CLI tools
    275,  # Mac stealers taxonomy (Atomic, Odyssey, Poseidon)
    278,  # Incident response in the age of AI
]

def reprocess_articles():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    print(f"\n{BColors.HEADER}{'='*80}{BColors.ENDC}")
    print(f"{BColors.HEADER}Reprocessing {len(MISCLASSIFIED_IDS)} Misclassified Articles{BColors.ENDC}")
    print(f"{BColors.HEADER}{'='*80}{BColors.ENDC}\n")
    
    for i, article_id in enumerate(MISCLASSIFIED_IDS, 1):
        # Fetch article details
        cur.execute("""
            SELECT id, title, url, content, published_date
            FROM articles
            WHERE id = ?
        """, (article_id,))
        
        row = cur.fetchone()
        if not row:
            print(f"{BColors.WARNING}[{i}/{len(MISCLASSIFIED_IDS)}] Article ID {article_id} not found{BColors.ENDC}")
            continue
        
        aid, title, url, content, published_date = row
        
        print(f"{BColors.OKBLUE}[{i}/{len(MISCLASSIFIED_IDS)}] Reprocessing:{BColors.ENDC}")
        print(f"  ID: {aid}")
        print(f"  Title: {title[:80]}...")
        print(f"  URL: {url}")
        
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
                import json
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
                
                print(f"  {BColors.OKGREEN}✓ Updated: {result['threat_risk']} | {result['category']}{BColors.ENDC}\n")
            else:
                print(f"  {BColors.WARNING}⚠ Analysis returned no result{BColors.ENDC}\n")
        
        except Exception as e:
            print(f"  {BColors.FAIL}✗ Error: {str(e)}{BColors.ENDC}\n")
            continue
    
    conn.close()
    
    print(f"\n{BColors.OKGREEN}{'='*80}{BColors.ENDC}")
    print(f"{BColors.OKGREEN}Reprocessing Complete{BColors.ENDC}")
    print(f"{BColors.OKGREEN}{'='*80}{BColors.ENDC}\n")
    
    log_success(f"Successfully reprocessed {len(MISCLASSIFIED_IDS)} articles")

if __name__ == '__main__':
    reprocess_articles()
