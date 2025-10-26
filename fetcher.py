# fetcher.py
import feedparser
import requests
import random
import socket
import sys
import datetime
from bs4 import BeautifulSoup
from config import RSS_FEEDS, MIN_ARTICLE_LENGTH, FETCH_TIMEOUT, SOCKET_TIMEOUT
from logging_utils import log_info, log_success, log_warn, log_error, BColors

USER_AGENTS = [
    'Mozilla/50.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/50.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/50.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/109.0 Safari/537.36',
]

def fetch_single_article(url):
    """Fetch and scrape a single article from a URL"""
    log_info(f"Fetching article from: {url}")
    
    try:
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        response = requests.get(url, headers=headers, timeout=FETCH_TIMEOUT)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try to extract title
        title = None
        if soup.find('h1'):
            title = soup.find('h1').get_text(strip=True)
        elif soup.find('title'):
            title = soup.find('title').get_text(strip=True)
        else:
            title = url.split('/')[-1].replace('-', ' ').title()
        
        # Try to extract article content
        content = ""
        
        # Try common article selectors
        article_selectors = [
            soup.find('article'),
            soup.find('div', class_='article-body'),
            soup.find('div', class_='article-content'),
            soup.find('div', class_='post-content'),
            soup.find('div', class_='entry-content'),
            soup.find('div', {'id': 'article-body'}),
            soup.find('main'),
        ]
        
        for selector in article_selectors:
            if selector:
                content = selector.get_text(separator='\n', strip=True)
                if len(content) > MIN_ARTICLE_LENGTH:
                    break
        
        # Fallback: get all paragraph text
        if len(content) < MIN_ARTICLE_LENGTH:
            paragraphs = soup.find_all('p')
            content = '\n'.join([p.get_text(strip=True) for p in paragraphs])
        
        article_data = {
            'title': title,
            'url': url,
            'published_date': datetime.date.today().isoformat(),
            'content': content
        }
        
        log_success(f"Successfully fetched: {title}")
        log_info(f"Content length: {len(content)} characters")
        
        return article_data
        
    except requests.RequestException as e:
        log_error(f"Failed to fetch article from {url}: {e}")
        return None
    except Exception as e:
        log_error(f"Error processing article from {url}: {e}")
        return None

def fetch_and_scrape_articles_sequential(existing_urls, start_date, end_date):
    all_articles = []
    log_info(f"Searching for new articles from {len(RSS_FEEDS)} sources for {start_date} to {end_date} ({(end_date - start_date).days + 1} days)...")
    
    # First pass: collect all entries and filter
    all_entries = []
    skipped_duplicates = 0
    skipped_outside_range = 0
    
    for feed_url in RSS_FEEDS:
        try:
            socket.setdefaulttimeout(SOCKET_TIMEOUT)
            feed = feedparser.parse(feed_url)
            socket.setdefaulttimeout(None)
            
            for entry in feed.entries:
                # Skip duplicates immediately
                if entry.link in existing_urls:
                    skipped_duplicates += 1
                    continue
                
                # Check date
                try:
                    published_date = entry.published_parsed
                    import datetime
                    published_date = datetime.date(*published_date[:3]) if published_date else datetime.date.today()
                except Exception:
                    import datetime
                    published_date = datetime.date.today()
                
                if start_date <= published_date <= end_date:
                    all_entries.append((entry, published_date))
                else:
                    skipped_outside_range += 1
                    
        except (socket.timeout, Exception) as e:
            log_warn(f"Could not process feed {feed_url}: {e}")
            socket.setdefaulttimeout(None)
    
    log_info(f"Found {len(all_entries)} new articles (skipped {skipped_duplicates} duplicates, {skipped_outside_range} outside date range)")
    
    # Second pass: fetch and scrape only new articles
    processed_articles = 0
    progress_bar_width = 50
    
    def print_progress_bar(current, total, phase_desc, messages=None):
        sys.stdout.write('\r' + ' ' * 100 + '\r')
        if messages:
            for msg in messages:
                print(msg)
        percent = int((current / total) * 100) if total else 100
        filled_length = int(progress_bar_width * percent // 100)
        bar = '█' * filled_length + '-' * (progress_bar_width - filled_length)
        sys.stdout.write(f"\r{phase_desc} |{bar}| {percent}% ({current}/{total})")
        sys.stdout.flush()

    if all_entries:
        print_progress_bar(0, len(all_entries), "Fetching Articles")
    
    status_messages = []
    for entry, published_date in all_entries:
        status_messages.append(f"{BColors.OKCYAN}[NEW]{BColors.ENDC} Fetched: {entry.title}")
        article_data = {'title': entry.title, 'url': entry.link, 'published_date': published_date.isoformat(), 'content': ""}
        
        if hasattr(entry, 'content') and entry.content:
            article_data['content'] = BeautifulSoup(entry.content[0].value, 'html.parser').get_text(strip=True)
        elif hasattr(entry, 'summary'):
            article_data['content'] = BeautifulSoup(entry.summary, 'html.parser').get_text(strip=True)
        
        if len(article_data['content']) < MIN_ARTICLE_LENGTH:
            try:
                headers = {'User-Agent': random.choice(USER_AGENTS)}
                response = requests.get(article_data['url'], headers=headers, timeout=FETCH_TIMEOUT)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                body = soup.find('article') or soup.find('div', class_='article-body')
                if body:
                    article_data['content'] = body.get_text(separator='\n', strip=True)
            except requests.RequestException:
                article_data['content'] = None
        
        all_articles.append(article_data)
        processed_articles += 1
        print_progress_bar(processed_articles, len(all_entries), "Fetching Articles", status_messages)
        status_messages = []
        
    sys.stdout.write('\n')
    sys.stdout.flush()
    log_success(f"Found a total of {len(all_articles)} new potential articles across all feeds.")
    return all_articles
