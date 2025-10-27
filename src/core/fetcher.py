# fetcher.py
import feedparser
import requests
import random
import socket
import sys
import datetime
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from src.config import RSS_FEEDS, MIN_ARTICLE_LENGTH, FETCH_TIMEOUT, SOCKET_TIMEOUT, THREADS_FETCH, ENABLE_PHASED_MULTITHREADING
from src.utils.logging_utils import log_info, log_success, log_warn, log_error, BColors, log_debug
from concurrent.futures import ThreadPoolExecutor, as_completed

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
    total_sources = len(RSS_FEEDS)
    checked_sources = 0

    def print_sources_progress(current, total, msg=None):
        width = 40
        percent = int((current / total) * 100) if total else 100
        filled = int(width * percent // 100)
        bar = '█' * filled + '-' * (width - filled)
        # Clear the current line without padding to avoid blank space/wrapping
        sys.stdout.write('\r\033[K')
        if msg:
            sys.stdout.write(f"{msg}\n")
        # Draw a single persistent progress bar line
        sys.stdout.write(f"Checking Sources |{bar}| {percent}% ({current}/{total})")
        sys.stdout.flush()
    
    if total_sources:
        print_sources_progress(0, total_sources)

    for idx, feed_url in enumerate(RSS_FEEDS, start=1):
        try:
            socket.setdefaulttimeout(SOCKET_TIMEOUT)
            feed = feedparser.parse(feed_url)
            socket.setdefaulttimeout(None)
            host = urlparse(feed_url).netloc or feed_url
            in_range_this = 0
            dupes_this = 0
            
            for entry in feed.entries:
                # Skip duplicates immediately
                if entry.link in existing_urls:
                    skipped_duplicates += 1
                    dupes_this += 1
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
                    in_range_this += 1
                else:
                    skipped_outside_range += 1

            checked_sources += 1
            print_sources_progress(
                checked_sources,
                total_sources,
                msg=f"{BColors.OKCYAN}[SOURCE]{BColors.ENDC} {host} — entries: {len(feed.entries)} | in-range: {in_range_this} | dupes: {dupes_this}"
            )
                    
        except (socket.timeout, Exception) as e:
            log_warn(f"Could not process feed {feed_url}: {e}")
            socket.setdefaulttimeout(None)
            checked_sources += 1
            host = urlparse(feed_url).netloc or feed_url
            print_sources_progress(
                checked_sources,
                total_sources,
                msg=f"{BColors.OKCYAN}[SOURCE]{BColors.ENDC} {host} — error: {str(e)[:80]}"
            )
    
    sys.stdout.write('\n')
    sys.stdout.flush()
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

def _process_entry(entry, published_date):
    """Build article data from an RSS entry and optionally fetch full content if too short."""
    article_data = {'title': entry.title, 'url': entry.link, 'published_date': published_date.isoformat(), 'content': ""}
    try:
        host = urlparse(entry.link).netloc
    except Exception:
        host = ''
    log_debug(f"Fetching: {entry.title[:80]}" + (f" [{host}]" if host else ""))
    try:
        if hasattr(entry, 'content') and entry.content:
            article_data['content'] = BeautifulSoup(entry.content[0].value, 'html.parser').get_text(strip=True)
        elif hasattr(entry, 'summary'):
            article_data['content'] = BeautifulSoup(entry.summary, 'html.parser').get_text(strip=True)

        # If content is short, try fetching the page
        if len(article_data['content']) < MIN_ARTICLE_LENGTH:
            headers = {'User-Agent': random.choice(USER_AGENTS)}
            response = requests.get(article_data['url'], headers=headers, timeout=FETCH_TIMEOUT)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            body = soup.find('article') or soup.find('div', class_='article-body') or soup.find('div', class_='article-content') or soup.find('main')
            if body:
                article_data['content'] = body.get_text(separator='\n', strip=True)
    except Exception:
        # On failure, keep whatever we had (may be empty)
        pass
    return article_data

def fetch_and_scrape_articles_parallel(existing_urls, start_date, end_date, max_workers=None):
    """Parallel version of fetch_and_scrape_articles using threads per entry.

    Phases remain: collect entries sequentially, then fetch/scrape entries concurrently.
    """
    all_articles = []
    log_info(f"Searching for new articles from {len(RSS_FEEDS)} sources for {start_date} to {end_date} ({(end_date - start_date).days + 1} days)...")

    # Phase A: collect entries
    all_entries = []
    skipped_duplicates = 0
    skipped_outside_range = 0
    total_sources = len(RSS_FEEDS)
    checked_sources = 0

    def print_sources_progress(current, total, msg=None):
        width = 40
        percent = int((current / total) * 100) if total else 100
        filled = int(width * percent // 100)
        bar = '█' * filled + '-' * (width - filled)
        # Clear the current line cleanly and reprint
        sys.stdout.write('\r\033[K')
        if msg:
            sys.stdout.write(f"{msg}\n")
        sys.stdout.write(f"Checking Sources |{bar}| {percent}% ({current}/{total})")
        sys.stdout.flush()

    if total_sources:
        print_sources_progress(0, total_sources)

    for idx, feed_url in enumerate(RSS_FEEDS, start=1):
        try:
            socket.setdefaulttimeout(SOCKET_TIMEOUT)
            feed = feedparser.parse(feed_url)
            socket.setdefaulttimeout(None)
            host = urlparse(feed_url).netloc or feed_url
            in_range_this = 0
            dupes_this = 0
            for entry in feed.entries:
                if entry.link in existing_urls:
                    skipped_duplicates += 1
                    dupes_this += 1
                    continue
                try:
                    published_date = entry.published_parsed
                    import datetime as _dt
                    published_date = _dt.date(*published_date[:3]) if published_date else _dt.date.today()
                except Exception:
                    import datetime as _dt
                    published_date = _dt.date.today()
                if start_date <= published_date <= end_date:
                    all_entries.append((entry, published_date))
                    in_range_this += 1
                else:
                    skipped_outside_range += 1
            checked_sources += 1
            print_sources_progress(
                checked_sources,
                total_sources,
                msg=f"{BColors.OKCYAN}[SOURCE]{BColors.ENDC} {host} — entries: {len(feed.entries)} | in-range: {in_range_this} | dupes: {dupes_this}"
            )
        except (socket.timeout, Exception) as e:
            log_warn(f"Could not process feed {feed_url}: {e}")
            socket.setdefaulttimeout(None)
            checked_sources += 1
            host = urlparse(feed_url).netloc or feed_url
            print_sources_progress(
                checked_sources,
                total_sources,
                msg=f"{BColors.OKCYAN}[SOURCE]{BColors.ENDC} {host} — error: {str(e)[:80]}"
            )

    total = len(all_entries)
    sys.stdout.write('\n')
    sys.stdout.flush()
    log_info(f"Found {total} new articles (skipped {skipped_duplicates} duplicates, {skipped_outside_range} outside date range)")

    if total == 0:
        return []

    # Phase B: process entries concurrently
    progress_bar_width = 50
    processed = 0

    def print_progress(current):
        percent = int((current / total) * 100) if total else 100
        filled_length = int(progress_bar_width * percent // 100)
        bar = '█' * filled_length + '-' * (progress_bar_width - filled_length)
        sys.stdout.write(f"\rFetching Articles |{bar}| {percent}% ({current}/{total})")
        sys.stdout.flush()

    print_progress(0)
    workers = max_workers or THREADS_FETCH
    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_entry = {executor.submit(_process_entry, entry, pub): (entry, pub) for entry, pub in all_entries}
        for future in as_completed(future_to_entry):
            try:
                result = future.result()
                all_articles.append(result)
            except Exception:
                pass
            processed += 1
            print_progress(processed)

    sys.stdout.write('\n')
    sys.stdout.flush()
    log_success(f"Found a total of {len(all_articles)} new potential articles across all feeds.")
    return all_articles
