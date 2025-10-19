# filtering.py
import requests
from tqdm import tqdm
from config import OLLAMA_MODEL, OLLAMA_HOST
from logging_utils import log_success, BColors

def filter_articles_sequential(articles):
    relevant_articles = []
    articles_to_check = [a for a in articles if a.get('content')]
    if not articles_to_check:
        return []
    for article in tqdm(articles_to_check, desc="Filtering for relevance"):
        if is_article_relevant_with_llm(article):
            relevant_articles.append(article)
            print(f"\n{BColors.OKGREEN}[RELEVANT]{BColors.ENDC} {article['title']}")
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
