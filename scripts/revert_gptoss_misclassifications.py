import sqlite3
import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.analysis import analyze_article_with_llm
from src.utils.logging_utils import log_info, log_success, BColors

DB_PATH = 'threat_intel.db'

# These IDs were incorrectly classified by gpt-oss:20b as INFORMATIONAL
# but should actually be NOT_RELEVANT (shopping, gadgets, consumer tech)
SHOULD_BE_NOT_RELEVANT = [
    233,  # The best 8 gizmos to gift
    234,  # Samsung smartwatch deal
    235,  # Windows PC recommendation
    236,  # PC crash solutions
    238,  # Apple Watch Ultra bands
    239,  # Gaming PC laptop
    240,  # Power bank
    241,  # Edge Copilot space heater
    243,  # Nintendo Switch
    244,  # iPad Pro M4
    246,  # Best Buy deals
    247,  # Black Friday iPad deals
    248,  # Windows 11 Snipping Tool
    249,  # Verizon internet plan
    250,  # Alibaba smart glasses
    251,  # Linux laptop
    252,  # Roku streaming
]

# These should legitimately be INFORMATIONAL (security-related)
SHOULD_BE_INFORMATIONAL = [
    199,  # Copilot Mico avatar
    200,  # Secure AI webinar
    202,  # Identity Security
    211,  # Ransomware preparedness survey
    212,  # Falcon Platform UX
    214,  # Falcon Exposure Management ExPRT.AI
    216,  # Falcon Insight ChromeOS
    217,  # Windows 10 End of Support
    227,  # ICE missile warheads (security policy)
    229,  # VPN reviews (security tools)
    231,  # Election infrastructure (security concern)
    232,  # VPN for iPhone (security tools)
    242,  # AI news accuracy (security awareness)
    245,  # OpenAI acquisition (tech/AI news)
    266,  # Cybersecurity acquisition deals
    267,  # Cyber-Intel Sharing Act
    276,  # Red Canary CFP tracker
    277,  # Red Canary Office Hours
]

def revert_misclassifications():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    print(f"\n{BColors.HEADER}{'='*80}{BColors.ENDC}")
    print(f"{BColors.HEADER}Reverting gpt-oss:20b Misclassifications{BColors.ENDC}")
    print(f"{BColors.HEADER}{'='*80}{BColors.ENDC}\n")
    
    # First, set the obvious non-security articles back to NOT_RELEVANT
    print(f"{BColors.OKBLUE}Setting {len(SHOULD_BE_NOT_RELEVANT)} consumer tech articles to NOT_RELEVANT...{BColors.ENDC}")
    for aid in SHOULD_BE_NOT_RELEVANT:
        cur.execute("""
            UPDATE articles
            SET threat_risk = 'NOT_RELEVANT',
                category = 'Not Cybersecurity Related'
            WHERE id = ?
        """, (aid,))
    conn.commit()
    print(f"{BColors.OKGREEN}✓ Done{BColors.ENDC}\n")
    
    # Reprocess the actual security-related articles with deepseek-coder
    print(f"{BColors.OKBLUE}Reprocessing {len(SHOULD_BE_INFORMATIONAL)} security articles with deepseek-coder-v2:16b...{BColors.ENDC}\n")
    
    success_count = 0
    
    for i, aid in enumerate(SHOULD_BE_INFORMATIONAL, 1):
        # Fetch article details
        cur.execute("""
            SELECT id, title, url, content, published_date
            FROM articles
            WHERE id = ?
        """, (aid,))
        
        row = cur.fetchone()
        if not row:
            print(f"{BColors.WARNING}[{i}/{len(SHOULD_BE_INFORMATIONAL)}] Article ID {aid} not found{BColors.ENDC}")
            continue
        
        aid, title, url, content, published_date = row
        
        print(f"{BColors.OKBLUE}[{i}/{len(SHOULD_BE_INFORMATIONAL)}] Reprocessing:{BColors.ENDC}")
        print(f"  ID: {aid}")
        print(f"  Title: {title[:70]}...")
        
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
                
                print(f"  {BColors.OKGREEN}✓ Updated: {result['threat_risk']} | {result['category']}{BColors.ENDC}\n")
                success_count += 1
            else:
                print(f"  {BColors.WARNING}⚠ Analysis returned no result{BColors.ENDC}\n")
        
        except Exception as e:
            print(f"  {BColors.FAIL}✗ Error: {str(e)}{BColors.ENDC}\n")
            continue
    
    conn.close()
    
    print(f"\n{BColors.OKGREEN}{'='*80}{BColors.ENDC}")
    print(f"{BColors.OKGREEN}Reversion Complete{BColors.ENDC}")
    print(f"{BColors.OKGREEN}NOT_RELEVANT articles restored: {len(SHOULD_BE_NOT_RELEVANT)}{BColors.ENDC}")
    print(f"{BColors.OKGREEN}Security articles reprocessed: {success_count}/{len(SHOULD_BE_INFORMATIONAL)}{BColors.ENDC}")
    print(f"{BColors.OKGREEN}{'='*80}{BColors.ENDC}\n")
    
    log_success(f"Successfully reverted misclassifications")

if __name__ == '__main__':
    revert_misclassifications()
