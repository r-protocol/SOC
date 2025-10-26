"""
Reprocess articles marked as NOT_RELEVANT with improved filter
This will update the database for articles that should have been relevant
"""
import sqlite3
import sys
import os
# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.filtering import is_article_relevant_with_llm
from src.utils.logging_utils import log_info, log_success, log_warn, BColors

def reprocess_not_relevant_articles(dry_run=True):
    """
    Re-evaluate articles marked as NOT_RELEVANT
    
    Args:
        dry_run: If True, only report what would change (don't update DB)
    """
    conn = sqlite3.connect('threat_intel.db')
    cursor = conn.cursor()
    
    # Get all NOT_RELEVANT articles
    cursor.execute('''
        SELECT id, title, content, url, published_date 
        FROM articles 
        WHERE threat_risk = 'NOT_RELEVANT'
        ORDER BY published_date DESC
    ''')
    
    articles = cursor.fetchall()
    total = len(articles)
    
    print(f"\n{'='*80}")
    print(f"🔄 Reprocessing {total} articles marked as NOT_RELEVANT")
    print(f"{'='*80}\n")
    
    if dry_run:
        print(f"{BColors.WARNING}DRY RUN MODE - No database changes will be made{BColors.ENDC}\n")
    else:
        print(f"{BColors.OKGREEN}LIVE MODE - Database will be updated{BColors.ENDC}\n")
    
    to_update = []
    still_not_relevant = []
    
    for i, (article_id, title, content, url, pub_date) in enumerate(articles, 1):
        # Progress indicator
        sys.stdout.write(f"\rProcessing: {i}/{total} ({i/total*100:.1f}%)")
        sys.stdout.flush()
        
        article_dict = {'title': title, 'content': content}
        is_relevant = is_article_relevant_with_llm(article_dict)
        
        if is_relevant:
            to_update.append((article_id, title, pub_date))
        else:
            still_not_relevant.append(title)
    
    sys.stdout.write('\n\n')
    
    # Print summary
    print(f"{'='*80}")
    print(f"📊 REPROCESSING RESULTS")
    print(f"{'='*80}\n")
    
    print(f"Total articles reviewed: {total}")
    print(f"Should be RELEVANT: {len(to_update)} ({len(to_update)/total*100:.1f}%)")
    print(f"Still NOT_RELEVANT: {len(still_not_relevant)} ({len(still_not_relevant)/total*100:.1f}%)")
    
    if to_update:
        print(f"\n{BColors.OKGREEN}✅ Articles to be reclassified as RELEVANT:{BColors.ENDC}")
        for article_id, title, pub_date in to_update[:20]:  # Show first 20
            print(f"  [{pub_date}] {title[:70]}")
        
        if len(to_update) > 20:
            print(f"  ... and {len(to_update) - 20} more")
    
    # Update database if not dry run
    if not dry_run and to_update:
        print(f"\n{BColors.WARNING}⚠️  Updating database...{BColors.ENDC}")
        
        for article_id, title, pub_date in to_update:
            # Clear the NOT_RELEVANT classification
            # These articles need to be re-analyzed to get proper threat_risk and category
            cursor.execute('''
                UPDATE articles 
                SET threat_risk = NULL, 
                    category = NULL,
                    summary = NULL,
                    recommendations = NULL
                WHERE id = ?
            ''', (article_id,))
        
        conn.commit()
        log_success(f"Updated {len(to_update)} articles - they will be re-analyzed on next run")
        
        print(f"\n{BColors.OKGREEN}✅ Database updated!{BColors.ENDC}")
        print(f"\n{BColors.OKBLUE}ℹ️  Next steps:{BColors.ENDC}")
        print(f"  1. Run: python main.py")
        print(f"  2. The {len(to_update)} articles will be re-analyzed with proper categorization")
        print(f"  3. They'll get correct threat_risk, category, and recommendations")
    
    elif dry_run and to_update:
        print(f"\n{BColors.OKBLUE}ℹ️  To apply these changes:{BColors.ENDC}")
        print(f"  python reprocess_not_relevant.py --apply")
    
    conn.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Reprocess NOT_RELEVANT articles')
    parser.add_argument('--apply', action='store_true', 
                       help='Apply changes to database (default is dry-run)')
    parser.add_argument('--dry-run', action='store_true', default=True,
                       help='Preview changes without modifying database (default)')
    
    args = parser.parse_args()
    
    # If --apply is specified, turn off dry_run
    dry_run = not args.apply
    
    reprocess_not_relevant_articles(dry_run=dry_run)
