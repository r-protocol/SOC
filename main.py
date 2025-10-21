# main.py
import sys
import datetime
from db_utils import initialize_database, get_existing_urls, store_analyzed_data, store_iocs, store_kql_queries
from fetcher import fetch_and_scrape_articles_sequential
from filtering import filter_articles_sequential
from analysis import analyze_articles_sequential
from report import generate_weekly_report, get_last_full_week_dates
from logging_utils import log_step, log_warn, log_info, log_success
from config import ENABLE_KQL_GENERATION, KQL_EXPORT_DIR, KQL_EXPORT_ENABLED
from kql_generator import IOCExtractor, KQLQueryGenerator, save_queries_to_file

def main_pipeline():
    # Parse the -n parameter if provided
    article_limit = None
    if "-n" in sys.argv:
        try:
            n_index = sys.argv.index("-n")
            if n_index + 1 < len(sys.argv):
                article_limit = int(sys.argv[n_index + 1])
        except (ValueError, IndexError):
            log_warn("Invalid -n parameter. Processing all articles.")

    initialize_database()
    existing_urls = get_existing_urls()
    start_date, end_date = get_last_full_week_dates()
    # Phase 1: Fetch and Scrape all new articles
    log_step(1, "Fetching and Scraping New Articles")
    new_articles = fetch_and_scrape_articles_sequential(existing_urls, start_date, end_date)
    
    # Apply article limit if specified
    if article_limit and len(new_articles) > article_limit:
        new_articles = new_articles[:article_limit]
        log_info(f"Limited to {article_limit} articles as requested.")
    # Phase 2: Filter for relevant articles
    log_step(2, "Filtering New Articles for Cybersecurity Relevance")
    relevant_articles = filter_articles_sequential(new_articles)
    if relevant_articles:
        # Phase 3: Analyze relevant articles
        log_step(3, "Analyzing New Relevant Articles with LLM")
        analyzed_data_list = analyze_articles_sequential(relevant_articles)
        
        if analyzed_data_list:
            # Phase 4: Store results in the database
            log_step(4, "Storing New Data in Database")
            article_ids = store_analyzed_data(analyzed_data_list)
            
            # Phase 5: Generate KQL Queries (if enabled)
            if ENABLE_KQL_GENERATION:
                log_step(5, "Generating KQL Threat Hunting Queries")
                extractor = IOCExtractor()
                generator = KQLQueryGenerator()
                
                total_iocs = 0
                total_queries = 0
                all_queries = []
                
                for article_id, article_data in article_ids:
                    # Extract IOCs
                    iocs = extractor.extract_all(article_data.get('content', ''))
                    ioc_count = sum(len(iocs[key]) for key in iocs)
                    
                    if ioc_count > 0:
                        # Store IOCs
                        stored_iocs = store_iocs(article_id, iocs)
                        total_iocs += stored_iocs
                        
                        # Generate KQL queries
                        queries = generator.generate_queries(article_data)
                        if queries:
                            stored_queries = store_kql_queries(article_id, queries)
                            total_queries += stored_queries
                            all_queries.extend(queries)
                            log_info(f"Generated {len(queries)} queries for '{article_data['title']}'")
                
                # Export queries to files if enabled
                if KQL_EXPORT_ENABLED and all_queries:
                    import os
                    os.makedirs(KQL_EXPORT_DIR, exist_ok=True)
                    save_queries_to_file(all_queries, KQL_EXPORT_DIR)
                
                log_success(f"KQL Generation complete: {total_iocs} IOCs, {total_queries} queries stored")
        else:
            log_warn("No new articles were successfully analyzed.")
    else:
        log_info("No new relevant articles to process.")
    
    # Phase 6: Generate the weekly report
    report_phase = 6 if ENABLE_KQL_GENERATION else 5
    log_step(report_phase, "Generating Weekly Report")
    generate_weekly_report()
    log_success("Pipeline finished successfully!")

if __name__ == "__main__":
    DEBUG_MODE = "-debug" in sys.argv
    main_pipeline()
