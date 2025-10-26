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
            # Update progress with new status message
            processed_articles += 1
            print_progress_bar(processed_articles, total_articles, "Filtering Articles", status_messages)
            status_messages = []
        else:
            # Skip irrelevant articles silently, just update progress
            processed_articles += 1
            print_progress_bar(processed_articles, total_articles, "Filtering Articles", None)
    sys.stdout.write('\n')  # End progress bar line
    sys.stdout.flush()
    log_success(f"Found {len(relevant_articles)} new relevant articles to analyze.")
    return relevant_articles

def is_article_relevant_with_llm(article):
    prompt = f"""
You are a cybersecurity threat intelligence analyst. Determine if this article is relevant to cybersecurity and security operations.

RELEVANT topics include:
- Vulnerabilities (CVE, exploits, zero-days, patches, PoC)
- Malware (ransomware, trojans, backdoors, infostealers, rootkits)
- Threat actors (APT groups, nation-state hackers, cybercrime groups)
- Security incidents (data breaches, attacks, compromises, leaks)
- Attack techniques (phishing, DDoS, supply chain, social engineering)
- Security tools and defenses (SIEM, EDR, firewalls, detection methods)
- Security advisories (CISA, vendor warnings, security bulletins)
- Network security (VPN flaws, router vulnerabilities, DNS attacks)
- Cloud security (AWS/Azure breaches, SaaS vulnerabilities)
- Authentication/Identity (credential theft, SSO attacks, MFA bypass)

NOT RELEVANT topics include:
- Consumer product reviews (phones, TVs, gaming consoles)
- General tech news (company earnings, stock prices, mergers)
- Non-security software updates (new features, UI changes)
- Entertainment and lifestyle content
- Shopping deals and price comparisons

IMPORTANT: If the title or content mentions vulnerabilities, exploits, attacks, hackers, breaches, malware, CVE numbers, or security flaws - it IS relevant.

Article Title: {article['title']}
Article Content: {article['content'][:1500]}

Is this article relevant to cybersecurity? Answer only YES or NO.
"""
    try:
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
            timeout=60
        )
        response.raise_for_status()
        response_text = response.json()['response'].strip().upper()
        
        # Debug: print response if not clear YES/NO
        if "YES" not in response_text and "NO" not in response_text:
            print(f"\n[DEBUG] Unexpected LLM response for '{article['title'][:50]}...': {response_text[:100]}")
        
        # More flexible YES detection
        is_relevant = "YES" in response_text or response_text.startswith("Y")
        
        return is_relevant
    except requests.RequestException as e:
        print(f"\n[DEBUG] LLM request failed for '{article['title'][:50]}...': {e}")
        return False
