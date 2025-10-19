# fetcher.py
import feedparser
import requests
import random
import socket
import sys
from bs4 import BeautifulSoup
from config import RSS_FEEDS
from logging_utils import log_info, log_success, log_warn, BColors

USER_AGENTS = [
    'Mozilla/50.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/50.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/50.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/109.0 Safari/537.36',
]

def fetch_and_scrape_articles_sequential(existing_urls, start_date, end_date):
    all_articles = []
    log_info(f"Searching for new articles from {len(RSS_FEEDS)} sources for the week of {start_date} to {end_date}...")
    total_feeds = len(RSS_FEEDS)
    total_articles = 0
    for feed_url in RSS_FEEDS:
        try:
            socket.setdefaulttimeout(20)
            feed = feedparser.parse(feed_url)
            socket.setdefaulttimeout(None)
            total_articles += len(feed.entries)
        except Exception:
            continue
    processed_articles = 0
    progress_bar_width = 50
    last_status_line = 0
    def print_progress_bar(current, total, phase_desc, messages=None):
        # First, clear the previous progress bar
        sys.stdout.write('\r' + ' ' * 100 + '\r')  # Clear line
        
        # Print any new status messages
        if messages:
            for msg in messages:
                print(msg)

        # Print the progress bar at the bottom
        percent = int((current / total) * 100) if total else 100
        filled_length = int(progress_bar_width * percent // 100)
        bar = '█' * filled_length + '-' * (progress_bar_width - filled_length)
        sys.stdout.write(f"\r{phase_desc} |{bar}| {percent}% ({current}/{total})")
        sys.stdout.flush()

    print_progress_bar(0, total_articles, "Fetching Articles")
    status_messages = []
    for feed_url in RSS_FEEDS:
        try:
            socket.setdefaulttimeout(20)
            feed = feedparser.parse(feed_url)
            socket.setdefaulttimeout(None)
            for entry in feed.entries:
                if entry.link in existing_urls:
                    continue
                try:
                    published_date = entry.published_parsed
                    import datetime
                    published_date = datetime.date(*published_date[:3]) if published_date else datetime.date.today()
                except Exception:
                    import datetime
                    published_date = datetime.date.today()
                if start_date <= published_date <= end_date:
                    status_messages.append(f"{BColors.OKCYAN}[NEW]{BColors.ENDC} Fetched: {entry.title}")
                    article_data = {'title': entry.title, 'url': entry.link, 'published_date': published_date.isoformat(), 'content': ""}
                    if hasattr(entry, 'content') and entry.content:
                        article_data['content'] = BeautifulSoup(entry.content[0].value, 'html.parser').get_text(strip=True)
                    elif hasattr(entry, 'summary'):
                        article_data['content'] = BeautifulSoup(entry.summary, 'html.parser').get_text(strip=True)
                    if len(article_data['content']) < 200:
                        try:
                            headers = {'User-Agent': random.choice(USER_AGENTS)}
                            response = requests.get(article_data['url'], headers=headers, timeout=15)
                            response.raise_for_status()
                            soup = BeautifulSoup(response.content, 'html.parser')
                            body = soup.find('article') or soup.find('div', class_='article-body')
                            if body:
                                article_data['content'] = body.get_text(separator='\n', strip=True)
                        except requests.RequestException:
                            article_data['content'] = None
                    all_articles.append(article_data)
                    processed_articles += 1
                    # Update progress with any new status messages
                    print_progress_bar(processed_articles, total_articles, "Fetching Articles", status_messages)
                    status_messages = []  # Clear after printing
        except (socket.timeout, Exception) as e:
            log_warn(f"Could not process feed {feed_url}: {e}")
            socket.setdefaulttimeout(None)
    sys.stdout.write('\n')  # End progress bar line
    sys.stdout.flush()
    log_success(f"Found a total of {len(all_articles)} new potential articles across all feeds.")
    return all_articles
