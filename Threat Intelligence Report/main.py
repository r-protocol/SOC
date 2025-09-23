# main.py
import sys
from utils import log_step, log_success, log_warn, log_info
from database import initialize_database, get_existing_urls, store_analyzed_data
from fetcher import fetch_and_scrape_articles_sequential
from analyzer import filter_articles_sequential, analyze_articles_sequential
from reporter import generate_weekly_report

# --- DEBUG MODE FLAG ---
DEBUG_MODE = False

def main_pipeline():
    """Main function to run the full, sequential per-phase pipeline."""
    initialize_database()
    existing_urls = get_existing_urls()
    
    # Phase 1: Fetch and Scrape all new articles
    log_step(1, "Fetching and Scraping New Articles")
    new_articles = fetch_and_scrape_articles_sequential(existing_urls)

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
            store_analyzed_data(analyzed_data_list)
        else:
            log_warn("No new articles were successfully analyzed.")
    else:
        log_info("No new relevant articles to process.")
        
    # Phase 5: Generate the weekly report regardless of whether new articles were found
    log_step(5, "Generating Weekly Report")
    generate_weekly_report()
    log_success("Pipeline finished successfully!")
    
if __name__ == "__main__":
    DEBUG_MODE = "-debug" in sys.argv
    main_pipeline()