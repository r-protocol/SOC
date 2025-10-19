# filtering.py
import requests
import sys
from config import OLLAMA_MODEL, OLLAMA_HOST
from logging_utils import log_success, BColors

def filter_articles_sequential(articles):
    relevant_articles = []
    articles_to_check = [a for a in articles if a.get('content')]
    if not articles_to_check:
        return []
    total_articles = len(articles_to_check)
    processed_articles = 0
    progress_bar_width = 50
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

    print_progress_bar(0, total_articles, "Filtering Articles")
    status_messages = []
    for article in articles_to_check:
        if is_article_relevant_with_llm(article):
            relevant_articles.append(article)
            status_messages.append(f"{BColors.OKGREEN}[RELEVANT]{BColors.ENDC} {article['title']}")
        processed_articles += 1
        # Update progress with any new status messages
        print_progress_bar(processed_articles, total_articles, "Filtering Articles", status_messages)
        status_messages = []  # Clear after printing
    sys.stdout.write('\n')  # End progress bar line
    sys.stdout.flush()
    log_success(f"Found {len(relevant_articles)} new relevant articles to analyze.")
    return relevant_articles

def is_article_relevant_with_llm(article):
    prompt = f"""
You are a cybersecurity news curator. Your task is to determine if the following article is related to cybersecurity.
Cybersecurity topics include vulnerabilities, data breaches, malware, ransomware, phishing, threat actors, cyber attacks, and security advisories.
General technology news, such as product releases (e.g., new phones or gaming features), company financials, or general IT trends, are NOT relevant.

Based on the title and content, is this article about cybersecurity? Respond with only a single word: YES or NO.

Article Title: {article['title']}
Article Content: {article['content'][:500]}
"""
    try:
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
            timeout=60
        )
        response.raise_for_status()
        response_text = response.json()['response'].strip().upper()
        return "YES" in response_text
    except requests.RequestException:
        return False
