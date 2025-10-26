# Improved Filtering Analysis
# This script tests different filtering approaches

import sqlite3
import requests
import sys
import os
# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config import OLLAMA_MODEL, OLLAMA_HOST

def test_improved_prompt():
    """Test improved filtering prompt on misclassified articles"""
    
    # Get the misclassified articles
    conn = sqlite3.connect('threat_intel.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT title, content, threat_risk, category 
        FROM articles 
        WHERE threat_risk = 'NOT_RELEVANT' 
        AND (
            title LIKE '%ransomware%' 
            OR title LIKE '%CVE%' 
            OR title LIKE '%vulnerability%'
            OR title LIKE '%CrowdStrike%'
            OR title LIKE '%Falcon%'
            OR title LIKE '%NTLM%'
            OR title LIKE '%authentication%'
            OR title LIKE '%malware%'
        )
        ORDER BY published_date DESC
        LIMIT 10
    ''')
    
    misclassified = cursor.fetchall()
    conn.close()
    
    print(f"🔍 Found {len(misclassified)} potentially misclassified articles\n")
    
    for i, (title, content, risk, category) in enumerate(misclassified, 1):
        print(f"\n{'='*80}")
        print(f"Article {i}: {title}")
        print(f"Current: [{risk}] {category}")
        print(f"{'='*80}")
        
        # Test with improved prompt
        result = test_with_improved_prompt(title, content[:2000])
        print(f"Improved Filter Result: {result}")
        
        if result:
            print("✅ SHOULD BE RELEVANT (currently marked NOT_RELEVANT)")
        else:
            print("❌ Correctly marked as NOT_RELEVANT")

def test_with_improved_prompt(title, content):
    """Test article with improved filtering logic"""
    
    prompt = f"""You are a cybersecurity expert analyzing articles for a Security Operations Center (SOC).

Determine if this article is relevant for security professionals and threat intelligence.

✅ ALWAYS RELEVANT - Mark as YES:
- Ransomware, malware, trojans, backdoors, infostealers, rootkits, botnets
- Vulnerabilities (CVE-####, exploits, zero-days, patches, security flaws)
- Threat actors (APT groups, nation-state hackers, cybercrime groups)
- Security incidents (breaches, attacks, compromises, hacks, intrusions)
- Attack techniques (phishing, DDoS, supply chain, social engineering, LOLBAS/Living-off-the-Land)
- Authentication attacks (NTLM, LDAP, credential theft, privilege escalation)
- Security products & vendor research (CrowdStrike, Falcon, Microsoft Defender, Sophos, etc.)
- Threat intelligence reports (eCrime landscape, APJ reports, threat analysis)
- Security features & protections (EDR, XDR, exposure management, automated response)
- Incident response & forensics (SOC operations, threat hunting, DFIR)
- Security advisories (CISA, vendor bulletins, end of support warnings)

❌ NOT RELEVANT - Mark as NO:
- Shopping deals, gift guides, product reviews (phones, TVs, gadgets)
- General tech news (earnings, stock prices, mergers) UNLESS security-related
- Entertainment (movies, games, streaming)
- Lifestyle (travel, food, fashion)
- General productivity software features UNLESS security-related

🔑 KEY RULE: If title contains these words, it's ALWAYS YES:
ransomware, malware, CVE, vulnerability, breach, exploit, hack, attack, threat, APT, 
phishing, authentication, NTLM, LDAP, credential, firewall, EDR, XDR, SOC, 
CrowdStrike, Falcon, privilege escalation, living-off-the-land, LOLBAS, eCrime

🔑 VENDOR SECURITY CONTENT = YES:
Any article from security vendors (CrowdStrike, Sophos, Microsoft Security, etc.) 
discussing threats, attacks, defenses, or security features is RELEVANT.

Article Title: {title}
Article Content (excerpt): {content}

Question: Is this article relevant for cybersecurity professionals and threat intelligence?
Answer with ONLY: YES or NO
"""
    
    try:
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
            timeout=60
        )
        response.raise_for_status()
        response_text = response.json()['response'].strip().upper()
        return "YES" in response_text or response_text.startswith("Y")
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    test_improved_prompt()
