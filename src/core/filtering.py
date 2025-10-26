# filtering.py
import requests
import sys
from src.config import OLLAMA_MODEL, OLLAMA_HOST
from src.utils.logging_utils import log_success, BColors

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
    # STEP 1: Pre-filter with critical keywords (catch obvious cybersecurity content)
    title_lower = article['title'].lower()
    content = article.get('content', '') or ''  # Handle None content
    content_preview = content[:1000].lower()
    
    # Critical keywords that ALWAYS mean cybersecurity relevance
    critical_keywords = [
        'ransomware', 'malware', 'cve-', 'vulnerability', 'zero-day', 'zero day',
        'exploit', 'breach', 'data breach', 'hack', 'hacked', 'attack', 'apt ',
        'threat actor', 'phishing', 'trojan', 'backdoor', 'rootkit', 'botnet',
        'ntlm', 'ldap', 'authentication bypass', 'privilege escalation',
        'living-off-the-land', 'lolbas', 'lolbins', 'ecrime', 'e-crime',
        'patch tuesday', 'security advisory', 'cisa alert', 'security bulletin',
        'credential theft', 'stolen credentials', 'supply chain attack',
        'nation-state', 'apt group', 'threat intelligence', 'ioc', 'indicator of compromise',
        'security flaw', 'remote code execution', 'arbitrary code execution',
        'ddos', 'denial of service', 'sql injection', 'xss', 'cross-site scripting'
    ]
    
    # Check title for critical keywords
    for keyword in critical_keywords:
        if keyword in title_lower:
            return True  # Skip LLM, definitely relevant
    
    # Check if from security vendor discussing threats/security
    security_vendor_keywords = [
        'crowdstrike', 'falcon platform', 'falcon insight', 'falcon defends',
        'falcon exposure', 'microsoft defender', 'microsoft sentinel',
        'sophos firewall', 'palo alto', 'unit 42', 'fortinet', 'fortigate',
        'check point', 'cisco talos', 'mandiant', 'proofpoint'
    ]
    
    for vendor in security_vendor_keywords:
        if vendor in title_lower:
            # If vendor + security terms, it's relevant
            security_terms = ['security', 'threat', 'attack', 'vulnerability', 'malware', 
                            'protection', 'defense', 'stops', 'detects', 'prevents']
            if any(term in title_lower or term in content_preview for term in security_terms):
                return True
    
    # STEP 2: Use LLM for edge cases (simplified prompt)
    prompt = f"""You are a cybersecurity expert analyzing articles for a Security Operations Center.

Is this article relevant for security professionals and threat intelligence?

✅ YES if about:
- Malware, ransomware, vulnerabilities, CVEs, exploits, breaches, attacks
- Threat actors, APT groups, cybercrime, nation-state hacking
- Security products/defenses (EDR, XDR, SIEM, firewalls, threat hunting)
- Attack techniques (phishing, LOLBAS, authentication bypass, privilege escalation)
- Security vendor research/reports (CrowdStrike, Sophos, Microsoft Security, etc.)
- Incident response, forensics, SOC operations
- Security advisories, patches, end-of-support warnings

❌ NO if about:
- Shopping deals, gift guides, product reviews (phones, TVs, gadgets)
- General tech news (earnings, mergers) unless security-related
- Entertainment, lifestyle, or non-security software features

Title: {article['title']}
Content (excerpt): {content[:1500]}

Is this relevant for cybersecurity professionals?
Answer ONLY: YES or NO
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
        # Fallback: Use keyword-based filtering if LLM fails
        return is_article_relevant_keywords(article)


def is_article_relevant_keywords(article):
    """Fallback keyword-based filtering when LLM is unavailable"""
    title_lower = article['title'].lower()
    content_lower = article.get('content', '').lower()[:3000]  # Check first 3000 chars
    combined = title_lower + " " + content_lower
    
    # First check for negative keywords in title (shopping/consumer content)
    negative_keywords_in_title = [
        'black friday', 'gift guide', 'best deals', 'price drop', 'walmart',
        'shop the', 'buy now', 'on sale', 'discount', 'smartwatch deal',
        'gift the person', 'best gizmos', 'best 8 gizmos', 'unboxing', 'best buy deals',
        'early deals', 'sales', 'nintendo switch', 'ipad pro', 'samsung smartwatch',
        'tech gift', 'holiday gift', 'apple watch bands', 'gaming pc guy',
        'power bank', 'space heater', 'windows pc i recommend', 'pc crash',
        'future-proof their tech careers', 'laptop changed my perspective'
    ]
    
    for keyword in negative_keywords_in_title:
        if keyword in title_lower:
            return False
    
    # HIGH PRIORITY: Keywords that DEFINITELY mean it's cybersecurity
    # Check TITLE FIRST for these critical terms
    critical_title_keywords = [
        'ransomware', 'malware', 'exploit', 'cve-', 'cve ', 'vulnerability',
        'zero-day', 'zero day', 'breach', 'hack', 'attack', 'threat',
        'phishing', 'ddos', 'crowdstrike', 'falcon', 'patch tuesday',
        'authentication bypass', 'privilege escalation', 'ntlm', 'ldap',
        'living-off-the-land', 'exposure management', 'endpoint detection',
        'threat landscape', 'ecrime', 'apt', 'security flaw'
    ]
    
    for keyword in critical_title_keywords:
        if keyword in title_lower:
            return True
    
    # Check for security vendor names in title (CrowdStrike, Falcon, etc.)
    vendor_keywords_in_title = [
        'crowdstrike', 'falcon platform', 'falcon insight', 'falcon defends',
        'falcon exposure', 'sophos firewall', 'palo alto', 'fortinet',
        'check point', 'cisco security', 'microsoft defender', 'sentinel',
        'kaspersky', 'bitdefender', 'trend micro', 'mcafee', 'eset'
    ]
    
    for vendor in vendor_keywords_in_title:
        if vendor in title_lower:
            return True
    
    # Security terms that indicate protective measures
    protection_keywords_in_title = [
        'how to stay protected', 'end of support', 'automated response',
        'security update', 'stops', 'defends against', 'predicts what attacker'
    ]
    
    for keyword in protection_keywords_in_title:
        if keyword in title_lower:
            return True
    
    # Extended cybersecurity keywords (check in title + content)
    extended_keywords = [
        'trojan', 'backdoor', 'rootkit', 'credential theft', 'security advisory',
        'cisa', 'intrusion', 'compromise', 'compromised', 'cybersecurity',
        'cyber security', 'infosec', 'threat intelligence', 'incident response',
        'forensics', 'siem', 'edr', 'xdr', 'firewall bypass',
        'remote code execution', 'sql injection', 'cross-site scripting',
        'buffer overflow', 'mitre att&ck', 'data breach', 'security patch',
        'nation-state', 'cyber attack', 'cyber threat', 'threat hunting',
        'soc ', 'security operation', 'git vulnerability', 'publicly disclosed',
        'lolbins', 'threat actor', 'botnet', 'domain user to system'
    ]
    
    for keyword in extended_keywords:
        if keyword in combined:
            return True
    
    # Default: If no keywords matched, it's not relevant
    return False
