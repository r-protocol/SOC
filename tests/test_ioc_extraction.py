import sys
import os
# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.fetcher import fetch_single_article
from src.core.kql_generator import IOCExtractor

url = "https://www.bleepingcomputer.com/news/security/cisa-updates-conti-ransomware-alert-with-nearly-100-domain-names/"
article = fetch_single_article(url)

extractor = IOCExtractor()
iocs = extractor.extract_all(article['content'])

print('\n' + '='*70)
print('REGEX IOC EXTRACTION RESULTS')
print('='*70)

for ioc_type, ioc_list in iocs.items():
    if ioc_list:
        print(f"\n{ioc_type.upper()}: {len(ioc_list)}")
        for ioc in ioc_list[:10]:
            value = ioc.get('value', str(ioc)) if isinstance(ioc, dict) else ioc
            print(f"  - {value}")
        if len(ioc_list) > 10:
            print(f"  ... and {len(ioc_list) - 10} more")

print('\n' + '='*70)
