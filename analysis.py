# analysis.py
import requests
import json
import re
import sys
from config import OLLAMA_MODEL, OLLAMA_HOST
from logging_utils import BColors

def repair_and_parse_json(raw_text):
    json_start = raw_text.find('{')
    json_end = raw_text.rfind('}')
    if json_start == -1 or json_end == -1:
        return None
    json_str = raw_text[json_start:json_end + 1]
    json_str = re.sub(r'}\s*{', '},{', json_str)
    json_str = re.sub(r',\s*([}\]])', r'\1', json_str)
    repaired_str = ""
    in_string = False
    for char in json_str:
        if char == '"':
            in_string = not in_string
        if in_string and char == '\n':
            repaired_str += '\\n'
        else:
            repaired_str += char
    json_str = repaired_str
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return None

def analyze_article_with_llm(article, retry_callback=None):
    prompt = f"""
You are a senior cybersecurity threat intelligence analyst. Your final output MUST be a single, valid, raw JSON object. Do not use markdown like ```json or **. Do not add any conversational text. The entire response must start with {{ and end with }}.

Analyze the following article and provide a threat assessment based on these strict definitions:
- **HIGH**: Active exploitation of a critical vulnerability, major data breach at a large company, or a widespread, severe malware campaign. Requires immediate action.
- **MEDIUM**: A significant vulnerability has been disclosed but isn't yet widely exploited, a smaller-scale breach, or a notable new malware variant. Requires timely review.
- **LOW**: A minor vulnerability, a theoretical attack vector, or a security advisory about a niche product. Should be monitored.
- **INFORMATIONAL**: General cybersecurity news, trend reports, or expert opinions that do not represent a direct threat. For awareness only.

1.  **summary**: A detailed, professional summary as a single JSON string, in a natural, narrative style (2-3 paragraphs, using "\\n\\n" for breaks). Explain what happened, why it's important, and the business impact.
2.  **threat_risk**: Must be one of: "HIGH", "MEDIUM", "LOW", "INFORMATIONAL".
3.  **category**: Must be one of: "Ransomware", "Phishing", "Vulnerability", "Malware", "Breach", "General Security".
4.  **recommendations**: A list of 5 actionable recommendations. Each must be a JSON object with two keys: a short "title" and a detailed "description".

Article Title: {article['title']}
Article Content: {article['content'][:8000]}
"""
    max_retries = 2
    for attempt in range(max_retries + 1):
        try:
            response = requests.post(
                f"{OLLAMA_HOST}/api/generate",
                json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
                timeout=300
            )
            response.raise_for_status()
            response_text = response.json()['response'].strip()
            parsed_json = repair_and_parse_json(response_text)
            if parsed_json:
                return parsed_json, None
            elif attempt < max_retries:
                retry_msg = f"{BColors.WARNING}[RETRYING]{BColors.ENDC} Invalid JSON for '{article['title']}' (Attempt {attempt + 2})"
                if retry_callback:
                    retry_callback(retry_msg)
                else:
                    print(f"\n{retry_msg}")
        except requests.RequestException:
            if attempt < max_retries:
                retry_msg = f"{BColors.WARNING}[RETRYING]{BColors.ENDC} Network error for '{article['title']}' (Attempt {attempt + 2})"
                if retry_callback:
                    retry_callback(retry_msg)
                else:
                    print(f"\n{retry_msg}")
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
