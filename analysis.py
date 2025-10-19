# analysis.py
import requests
import json
import re
from tqdm import tqdm
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

def analyze_article_with_llm(article):
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
                return parsed_json
            elif attempt < max_retries:
                print(f"\n{BColors.WARNING}[RETRYING]{BColors.ENDC} Invalid JSON for '{article['title']}' (Attempt {attempt + 2})")
        except requests.RequestException:
            if attempt < max_retries:
                print(f"\n{BColors.WARNING}[RETRYING]{BColors.ENDC} Network error for '{article['title']}' (Attempt {attempt + 2})")
    return None

def analyze_articles_sequential(articles):
    analyzed_articles = []
    for article in tqdm(articles, desc="Analyzing articles"):
        llm_analysis = analyze_article_with_llm(article)
        if llm_analysis:
            article.update(llm_analysis)
            analyzed_articles.append(article)
            print(f"\n{BColors.OKGREEN}[ANALYZED]{BColors.ENDC} {article['title']} (Risk: {article.get('threat_risk')})")
    return analyzed_articles
