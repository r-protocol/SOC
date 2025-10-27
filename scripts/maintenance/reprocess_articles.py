"""
Unified Article Reprocessing Script

This script consolidates all article reprocessing functionality:
- Reprocess specific articles by ID
- Reprocess articles by risk level (NOT_RELEVANT, LOW, MEDIUM, HIGH, INFORMATIONAL)
- Reprocess articles by category
- Bulk reprocessing operations

Usage:
    python reprocess_articles.py --ids 210 213 215        # Specific IDs
    python reprocess_articles.py --risk NOT_RELEVANT      # All NOT_RELEVANT articles
    python reprocess_articles.py --category "Malware"     # All articles in category
    python reprocess_articles.py --all                    # Reprocess everything (use with caution)
"""

import sqlite3
import sys
import os
import json
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.analysis import analyze_article_with_llm
from src.utils.logging_utils import log_info, log_success, log_warning, BColors

DB_PATH = 'threat_intel.db'


def get_articles_to_reprocess(conn, ids=None, risk=None, category=None, reprocess_all=False):
    """Fetch articles based on criteria"""
    cur = conn.cursor()
    
    if ids:
        placeholders = ','.join('?' * len(ids))
        query = f"""
            SELECT id, title, url, content, published_date
            FROM articles
            WHERE id IN ({placeholders})
            ORDER BY id
        """
        cur.execute(query, ids)
    elif risk:
        query = """
            SELECT id, title, url, content, published_date
            FROM articles
            WHERE threat_risk = ?
            ORDER BY id
        """
        cur.execute(query, (risk,))
    elif category:
        query = """
            SELECT id, title, url, content, published_date
            FROM articles
            WHERE category = ?
            ORDER BY id
        """
        cur.execute(query, (category,))
    elif reprocess_all:
        query = """
            SELECT id, title, url, content, published_date
            FROM articles
            ORDER BY id
        """
        cur.execute(query)
    else:
        return []
    
    return cur.fetchall()


def reprocess_article(conn, aid, title, url, content, published_date, show_progress=True):
    """Reprocess a single article"""
    if show_progress:
        print(f"  ID: {aid}")
        print(f"  Title: {title[:70]}...")
    
    # Create article dict for analysis
    article = {
        'title': title,
        'url': url,
        'content': content,
        'published_date': published_date
    }
    
    try:
        result, _ = analyze_article_with_llm(article)
        
        if result:
            # Convert recommendations to JSON string if it's a list
            recommendations_str = json.dumps(result.get('recommendations', [])) if isinstance(result.get('recommendations'), list) else result.get('recommendations', '')
            
            # Update the database
            cur = conn.cursor()
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
            
            if show_progress:
                print(f"  {BColors.OKGREEN}✓ Updated: {result['threat_risk']} | {result['category']}{BColors.ENDC}\n")
            
            return True, result
        else:
            if show_progress:
                print(f"  {BColors.WARNING}⚠ Analysis returned no result{BColors.ENDC}\n")
            return False, None
    
    except Exception as e:
        if show_progress:
            print(f"  {BColors.FAIL}✗ Error: {str(e)}{BColors.ENDC}\n")
        return False, None


def main():
    parser = argparse.ArgumentParser(
        description='Reprocess articles with LLM analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --ids 210 213 215                    # Reprocess specific articles
  %(prog)s --risk NOT_RELEVANT                  # Reprocess all NOT_RELEVANT articles
  %(prog)s --category "Malware"                 # Reprocess all Malware articles
  %(prog)s --risk HIGH --dry-run                # See what would be reprocessed
        """
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--ids', nargs='+', type=int, help='Specific article IDs to reprocess')
    group.add_argument('--risk', choices=['HIGH', 'MEDIUM', 'LOW', 'INFORMATIONAL', 'NOT_RELEVANT'],
                       help='Reprocess all articles with this risk level')
    group.add_argument('--category', type=str, help='Reprocess all articles in this category')
    group.add_argument('--all', action='store_true', help='Reprocess ALL articles (use with caution!)')
    
    parser.add_argument('--dry-run', action='store_true', help='Show what would be reprocessed without doing it')
    parser.add_argument('--quiet', action='store_true', help='Minimal output')
    
    args = parser.parse_args()
    
    conn = sqlite3.connect(DB_PATH)
    
    # Get articles to reprocess
    articles = get_articles_to_reprocess(
        conn,
        ids=args.ids,
        risk=args.risk,
        category=args.category,
        reprocess_all=args.all
    )
    
    if not articles:
        print(f"{BColors.WARNING}No articles found matching criteria{BColors.ENDC}")
        conn.close()
        return
    
    total = len(articles)
    
    # Determine criteria description
    if args.ids:
        criteria = f"IDs: {', '.join(map(str, args.ids))}"
    elif args.risk:
        criteria = f"Risk: {args.risk}"
    elif args.category:
        criteria = f"Category: {args.category}"
    else:
        criteria = "ALL ARTICLES"
    
    if not args.quiet:
        print(f"\n{BColors.HEADER}{'='*80}{BColors.ENDC}")
        print(f"{BColors.HEADER}Article Reprocessing - {criteria}{BColors.ENDC}")
        print(f"{BColors.HEADER}{'='*80}{BColors.ENDC}\n")
        print(f"Found {total} article(s) to reprocess\n")
    
    if args.dry_run:
        print(f"{BColors.OKBLUE}DRY RUN - Articles that would be reprocessed:{BColors.ENDC}\n")
        for aid, title, url, _, date in articles:
            print(f"  [{aid}] {title[:70]}...")
            print(f"       {date} | {url}\n")
        conn.close()
        return
    
    # Confirm if processing many articles
    if total > 20 and not args.quiet:
        response = input(f"{BColors.WARNING}About to reprocess {total} articles. Continue? (y/N): {BColors.ENDC}")
        if response.lower() != 'y':
            print("Cancelled")
            conn.close()
            return
    
    # Process articles
    success_count = 0
    error_count = 0
    
    for i, (aid, title, url, content, published_date) in enumerate(articles, 1):
        if not args.quiet:
            print(f"{BColors.OKBLUE}[{i}/{total}] Reprocessing:{BColors.ENDC}")
        
        success, result = reprocess_article(
            conn, aid, title, url, content, published_date,
            show_progress=not args.quiet
        )
        
        if success:
            success_count += 1
        else:
            error_count += 1
    
    conn.close()
    
    if not args.quiet:
        print(f"\n{BColors.OKGREEN}{'='*80}{BColors.ENDC}")
        print(f"{BColors.OKGREEN}Reprocessing Complete{BColors.ENDC}")
        print(f"{BColors.OKGREEN}Successfully processed: {success_count}/{total}{BColors.ENDC}")
        if error_count > 0:
            print(f"{BColors.WARNING}Errors: {error_count}{BColors.ENDC}")
        print(f"{BColors.OKGREEN}{'='*80}{BColors.ENDC}\n")
    
    log_success(f"Reprocessed {success_count}/{total} articles")


if __name__ == '__main__':
    main()
