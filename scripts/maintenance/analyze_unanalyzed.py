"""
Analyze articles that have NULL threat_risk (unanalyzed or reset articles)
"""
import sqlite3
import sys
import os
# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.analysis import analyze_articles_sequential
from src.utils.db_utils import store_analyzed_data, store_iocs, store_kql_queries, DATABASE_PATH
from src.utils.logging_utils import log_info, log_success, BColors
from src.config import ENABLE_KQL_GENERATION
from src.core.kql_generator_llm import LLMKQLGenerator

def analyze_unanalyzed_articles():
    """Find and analyze articles with NULL threat_risk"""
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Get articles that need analysis (NULL threat_risk)
    cursor.execute('''
        SELECT id, title, url, published_date, content
        FROM articles
        WHERE threat_risk IS NULL
        ORDER BY published_date DESC
    ''')
    
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        log_info("No articles need analysis.")
        return
    
    print(f"\n{BColors.HEADER}{'='*70}{BColors.ENDC}")
    print(f"{BColors.OKCYAN}📊 Found {len(rows)} articles to analyze{BColors.ENDC}")
    print(f"{BColors.HEADER}{'='*70}{BColors.ENDC}\n")
    
    # Convert to article dicts
    articles = []
    for row in rows:
        article_id, title, url, pub_date, content = row
        articles.append({
            'id': article_id,
            'title': title,
            'url': url,
            'published_date': pub_date,
            'content': content
        })
    
    # Analyze articles
    print(f"\n{BColors.OKBLUE}--- Analyzing Articles ---{BColors.ENDC}\n")
    analyzed_articles = analyze_articles_sequential(articles)
    
    if not analyzed_articles:
        log_info("No articles were successfully analyzed.")
        return
    
    # Store results
    print(f"\n{BColors.OKBLUE}--- Storing Analysis Results ---{BColors.ENDC}\n")
    stored_count = 0
    
    for article in analyzed_articles:
        if store_analyzed_data(article):
            stored_count += 1
            risk = article.get('threat_risk', 'UNKNOWN')
            category = article.get('category', 'Unknown')
            log_success(f"Stored: {article['title'][:60]} [{risk} | {category}]")
    
    log_success(f"\n✅ Analysis complete: {stored_count}/{len(analyzed_articles)} articles stored")
    
    # Optional: Generate KQL queries
    if ENABLE_KQL_GENERATION and analyzed_articles:
        print(f"\n{BColors.OKBLUE}--- Generating KQL Queries ---{BColors.ENDC}\n")
        generate_kql_for_analyzed_articles(analyzed_articles)

def generate_kql_for_analyzed_articles(articles):
    """Generate KQL queries for analyzed articles"""
    llm_generator = LLMKQLGenerator()
    
    total_iocs = 0
    total_queries = 0
    
    for article in articles:
        # Skip if no IOCs likely
        if article.get('threat_risk') in ['INFORMATIONAL', 'NOT_RELEVANT']:
            continue
        
        iocs, queries = llm_generator.generate_all(article)
        ioc_count = sum(len(iocs.get(key, [])) for key in iocs)
        
        if ioc_count > 0:
            stored_iocs = store_iocs(article['id'], iocs)
            total_iocs += stored_iocs
        
        if queries:
            stored_queries = store_kql_queries(article['id'], queries)
            total_queries += stored_queries
            log_info(f"Generated {len(queries)} queries for '{article['title'][:50]}'")
    
    log_success(f"KQL Generation: {total_iocs} IOCs, {total_queries} queries stored")

if __name__ == "__main__":
    analyze_unanalyzed_articles()
