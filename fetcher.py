# fetcher.py
import feedparser
import requests
import random
import socket
from bs4 import BeautifulSoup
from tqdm import tqdm
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
    for feed_url in tqdm(RSS_FEEDS, desc="Fetching from feeds"):
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
                    print(f"\n{BColors.OKCYAN}[NEW]{BColors.ENDC} Fetched: {entry.title}")
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
        except (socket.timeout, Exception) as e:
            log_warn(f"Could not process feed {feed_url}: {e}")
            socket.setdefaulttimeout(None)
    log_success(f"Found a total of {len(all_articles)} new potential articles across all feeds.")
    return all_articles
