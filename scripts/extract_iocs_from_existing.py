"""
Extract IOCs from all existing articles in the database
This script will go through all analyzed articles and extract IOCs using the LLM
"""

import sys
import os
import sqlite3

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.kql_generator_llm import LLMKQLGenerator
from src.utils.db_utils import store_iocs, store_kql_queries, DATABASE_PATH
from src.utils.logging_utils import log_step, log_success, log_info, log_error, log_warn, BColors


def extract_iocs_from_all_articles(limit=None, with_kql=True, risk_filter=None):
    """
    Extract IOCs from all articles in the database
    
    Args:
        limit: Maximum number of articles to process (None = all)
        with_kql: Also generate KQL queries (default: True)
        risk_filter: Only process articles with specific risk level (e.g., 'HIGH', 'MEDIUM')
    """
    print(f"\n{BColors.BOLD}{'='*70}{BColors.ENDC}")
    print(f"{BColors.BOLD}🔍 IOC Extraction from Existing Articles{BColors.ENDC}")
    print(f"{BColors.BOLD}{'='*70}{BColors.ENDC}\n")
    
    # Step 1: Get all articles from database
    log_step(1, "Fetching articles from database")
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Build query
    query = """
        SELECT id, title, url, content, summary, category, threat_risk, published_date
        FROM articles
        WHERE category != 'Not Cybersecurity Related'
        AND threat_risk != 'NOT_RELEVANT'
        AND threat_risk != 'UNANALYZED'
        AND content IS NOT NULL
        AND content != ''
    """
    
    if risk_filter:
        query += f" AND threat_risk = '{risk_filter.upper()}'"
    
    query += " ORDER BY published_date DESC"
    
    if limit:
        query += f" LIMIT {limit}"
    
    cursor.execute(query)
    articles = cursor.fetchall()
    conn.close()
    
    if not articles:
        log_warn("No articles found matching criteria")
        return
    
    log_success(f"Found {len(articles)} articles to process")
    
    if risk_filter:
        log_info(f"Filtering by risk level: {risk_filter}")
    
    # Step 2: Initialize LLM generator
    log_step(2, "Initializing LLM IOC Extractor")
    generator = LLMKQLGenerator()
    
    # Step 3: Process each article
    log_step(3, f"Extracting IOCs from {len(articles)} articles")
    
    total_iocs = 0
    total_queries = 0
    articles_with_iocs = 0
    articles_with_queries = 0
    failed_articles = []
    
    for i, row in enumerate(articles, 1):
        article_id, title, url, content, summary, category, threat_risk, published_date = row
        
        print(f"\n{BColors.OKCYAN}[{i}/{len(articles)}]{BColors.ENDC} Processing: {title[:60]}...")
        print(f"  Risk: {threat_risk} | Category: {category}")
        
        # Prepare article dict
        article = {
            'id': article_id,
            'title': title,
            'url': url,
            'content': content,
            'summary': summary,
            'category': category,
            'threat_risk': threat_risk,
            'published_date': published_date
        }
        
        try:
            # Extract IOCs
            if with_kql:
                # Extract IOCs and generate queries in one go
                iocs, queries = generator.generate_all(article)
            else:
                # Just extract IOCs, no queries
                iocs = generator.extract_iocs_with_llm(article)
                queries = []
            
            # Count IOCs
            ioc_count = sum(len(iocs.get(key, [])) for key in iocs)
            
            if ioc_count > 0:
                # Store IOCs
                stored = store_iocs(article_id, iocs)
                total_iocs += stored
                articles_with_iocs += 1
                print(f"  {BColors.OKGREEN}✓{BColors.ENDC} Extracted {stored} IOCs")
                
                # Show breakdown
                for ioc_type, ioc_list in iocs.items():
                    if ioc_list:
                        print(f"    - {ioc_type}: {len(ioc_list)}")
            else:
                print(f"  {BColors.WARNING}○{BColors.ENDC} No IOCs found")
            
            # Store KQL queries if generated
            if with_kql and queries:
                stored_queries = store_kql_queries(article_id, queries)
                total_queries += stored_queries
                articles_with_queries += 1
                print(f"  {BColors.OKGREEN}✓{BColors.ENDC} Generated {stored_queries} KQL queries")
            
        except Exception as e:
            log_error(f"Failed to process article {article_id}: {e}")
            failed_articles.append((article_id, title, str(e)))
            continue
    
    # Step 4: Summary
    print(f"\n{BColors.BOLD}{'='*70}{BColors.ENDC}")
    print(f"{BColors.BOLD}📊 Extraction Summary{BColors.ENDC}")
    print(f"{BColors.BOLD}{'='*70}{BColors.ENDC}")
    print(f"{BColors.OKGREEN}Total articles processed:{BColors.ENDC} {len(articles)}")
    print(f"{BColors.OKGREEN}Articles with IOCs:{BColors.ENDC} {articles_with_iocs}")
    print(f"{BColors.OKGREEN}Total IOCs extracted:{BColors.ENDC} {total_iocs}")
    
    if with_kql:
        print(f"{BColors.OKGREEN}Articles with queries:{BColors.ENDC} {articles_with_queries}")
        print(f"{BColors.OKGREEN}Total KQL queries:{BColors.ENDC} {total_queries}")
    
    if failed_articles:
        print(f"\n{BColors.FAIL}Failed articles:{BColors.ENDC} {len(failed_articles)}")
        for article_id, title, error in failed_articles[:5]:
            print(f"  - [{article_id}] {title[:50]}... ({error[:50]})")
    
    print(f"{BColors.BOLD}{'='*70}{BColors.ENDC}\n")
    
    log_success("IOC extraction complete!")


def main():
    """Parse arguments and run extraction"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Extract IOCs from existing articles in database')
    parser.add_argument('-n', '--limit', type=int, help='Maximum number of articles to process')
    parser.add_argument('--no-kql', action='store_true', help='Extract IOCs only, skip KQL generation')
    parser.add_argument('--risk', choices=['HIGH', 'MEDIUM', 'LOW', 'INFORMATIONAL'], 
                       help='Filter by risk level')
    parser.add_argument('--high-only', action='store_true', help='Process only HIGH risk articles')
    
    args = parser.parse_args()
    
    # Determine risk filter
    risk_filter = None
    if args.high_only:
        risk_filter = 'HIGH'
    elif args.risk:
        risk_filter = args.risk
    
    # Run extraction
    extract_iocs_from_all_articles(
        limit=args.limit,
        with_kql=not args.no_kql,
        risk_filter=risk_filter
    )


if __name__ == "__main__":
    main()
