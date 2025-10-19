# analysis.py
import requests
import json
import re
import sys
from config import OLLAMA_MODEL, OLLAMA_HOST
from logging_utils import BColors

def repair_and_parse_json(raw_text, debug_title=None):
    """Enhanced JSON repair with multiple strategies"""
    
    # Strategy 1: Find JSON boundaries
    json_start = raw_text.find('{')
    json_end = raw_text.rfind('}')
    if json_start == -1 or json_end == -1:
        return None
    
    json_str = raw_text[json_start:json_end + 1]
    
    # Strategy 2: Remove markdown code blocks if present
    json_str = re.sub(r'```json\s*', '', json_str)
    json_str = re.sub(r'```\s*', '', json_str)
    
    # Strategy 3: Fix common JSON issues
    json_str = re.sub(r'}\s*{', '},{', json_str)  # Multiple objects
    json_str = re.sub(r',\s*([}\]])', r'\1', json_str)  # Trailing commas
    
    # Strategy 4: Handle newlines in strings
    repaired_str = ""
    in_string = False
    escape_next = False
    for i, char in enumerate(json_str):
        if escape_next:
            repaired_str += char
            escape_next = False
            continue
        
        if char == '\\':
            escape_next = True
            repaired_str += char
            continue
            
        if char == '"' and (i == 0 or json_str[i-1] != '\\'):
            in_string = not in_string
            repaired_str += char
        elif in_string and char == '\n':
            repaired_str += '\\n'
        elif in_string and char == '\r':
            continue  # Skip carriage returns
        elif in_string and char == '\t':
            repaired_str += '\\t'
        else:
            repaired_str += char
    
    json_str = repaired_str
    
    # Strategy 5: Try to parse
    try:
        parsed = json.loads(json_str)
        # Validate structure
        required_keys = ['summary', 'threat_risk', 'category', 'recommendations']
        if all(key in parsed for key in required_keys):
            return parsed
        else:
            if debug_title:
                print(f"\n[DEBUG] Missing required keys for '{debug_title}'. Found: {list(parsed.keys())}")
            return None
    except json.JSONDecodeError as e:
        if debug_title:
            # Save failed JSON for debugging
            try:
                with open('failed_json_debug.txt', 'a', encoding='utf-8') as f:
                    f.write(f"\n\n=== FAILED: {debug_title} ===\n")
                    f.write(f"Error: {str(e)}\n")
                    f.write(f"JSON attempt:\n{json_str[:500]}...\n")
            except:
                pass
        return None

def analyze_article_with_llm(article, retry_callback=None):
    prompt = f"""You are a cybersecurity threat intelligence analyst. You must respond ONLY with valid JSON. No markdown, no explanations, no extra text.

CRITICAL RULES:
1. Response must start with {{ and end with }}
2. All strings must use double quotes "
3. Escape special characters in strings (quotes, newlines, etc.)
4. No trailing commas
5. Use \\n\\n for paragraph breaks in the summary field

Required JSON structure:
{{
  "summary": "Professional summary here. Use \\n\\n for paragraph breaks. 2-3 paragraphs about the threat, its impact, and business implications.",
  "threat_risk": "HIGH or MEDIUM or LOW or INFORMATIONAL",
  "category": "Ransomware or Phishing or Vulnerability or Malware or Breach or General Security",
  "recommendations": [
    {{"title": "Short action title", "description": "Detailed description"}},
    {{"title": "Short action title", "description": "Detailed description"}},
    {{"title": "Short action title", "description": "Detailed description"}},
    {{"title": "Short action title", "description": "Detailed description"}},
    {{"title": "Short action title", "description": "Detailed description"}}
  ]
}}

THREAT RISK DEFINITIONS:
- HIGH: Active exploitation, critical vulnerability, major breach, widespread malware. Immediate action required.
- MEDIUM: Disclosed vulnerability (not widely exploited), smaller breach, new malware variant. Timely review needed.
- LOW: Minor vulnerability, theoretical attack, niche product advisory. Monitor only.
- INFORMATIONAL: General news, trends, opinions. No direct threat. Awareness only.

ARTICLE TO ANALYZE:
Title: {article['title']}
Content: {article['content'][:8000]}

RESPOND WITH JSON ONLY:"""

    max_retries = 2
    for attempt in range(max_retries + 1):
        try:
            # Use lower temperature for more consistent output
            response = requests.post(
                f"{OLLAMA_HOST}/api/generate",
                json={
                    "model": OLLAMA_MODEL, 
                    "prompt": prompt, 
                    "stream": False,
                    "options": {
                        "temperature": 0.3,  # Lower = more consistent
                        "top_p": 0.9
                    }
                },
                timeout=300
            )
            response.raise_for_status()
            response_text = response.json()['response'].strip()
            
            # Try to parse with debug info
            parsed_json = repair_and_parse_json(response_text, debug_title=article['title'])
            
            if parsed_json:
                return parsed_json, None
            elif attempt < max_retries:
                retry_msg = f"{BColors.WARNING}[RETRYING]{BColors.ENDC} Invalid JSON for '{article['title']}' (Attempt {attempt + 2})"
                if retry_callback:
                    retry_callback(retry_msg)
                else:
                    print(f"\n{retry_msg}")
        except requests.RequestException as e:
            if attempt < max_retries:
                retry_msg = f"{BColors.WARNING}[RETRYING]{BColors.ENDC} Network error for '{article['title']}' (Attempt {attempt + 2})"
                if retry_callback:
                    retry_callback(retry_msg)
                else:
                    print(f"\n{retry_msg}")
    
    # All retries failed
    if retry_callback:
        retry_callback(f"{BColors.FAIL}[FAILED]{BColors.ENDC} Could not analyze '{article['title']}' after {max_retries + 1} attempts")
    return None, None

def analyze_articles_sequential(articles):
    analyzed_articles = []
    total_articles = len(articles)
    processed_articles = 0
    progress_bar_width = 50
    last_line = ""
    status_messages = []
    
    def update_progress(current, total, phase_desc):
        nonlocal last_line
        
        # Create the progress bar
        percent = int((current / total) * 100) if total else 100
        filled_length = int(progress_bar_width * percent // 100)
        bar = '█' * filled_length + '-' * (progress_bar_width - filled_length)
        progress = f"{phase_desc} |{bar}| {percent}% ({current}/{total})"
        
        # Clear previous progress bar line
        if last_line:
            sys.stdout.write('\r' + ' ' * len(last_line) + '\r')
            sys.stdout.flush()
        
        # Print progress bar
        sys.stdout.write(progress)
        sys.stdout.flush()
        last_line = progress
    
    def handle_message(msg):
        """Callback to handle retry/status messages"""
        nonlocal last_line
        # Clear current progress bar
        if last_line:
            sys.stdout.write('\r' + ' ' * len(last_line) + '\r')
            sys.stdout.flush()
        # Print the message
        print(msg)
        # Redraw the progress bar
        update_progress(processed_articles, total_articles, "Analyzing Articles")

    update_progress(0, total_articles, "Analyzing Articles")
    
    for article in articles:
        llm_analysis, _ = analyze_article_with_llm(article, retry_callback=handle_message)
        if llm_analysis:
            article.update(llm_analysis)
            analyzed_articles.append(article)
            # Print success message
            success_msg = f"{BColors.OKGREEN}[ANALYZED]{BColors.ENDC} {article['title']} (Risk: {article.get('threat_risk')})"
            handle_message(success_msg)
        
        processed_articles += 1
        update_progress(processed_articles, total_articles, "Analyzing Articles")
    
    sys.stdout.write('\n')  # End progress bar line
    sys.stdout.flush()
    return analyzed_articles
