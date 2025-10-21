# kql_generator.py
"""
KQL Query Generator for Threat Intelligence
Generates Kusto Query Language (KQL) queries from analyzed threat intelligence articles
Supports: Microsoft Sentinel, Microsoft Defender, Azure Log Analytics
"""

import re
import json
from typing import Dict, List, Optional, Tuple
from logging_utils import log_info, log_success, log_warn, log_error, BColors

# ============================================================================
# PHASE 1: IOC EXTRACTION
# ============================================================================

class IOCExtractor:
    """Extract Indicators of Compromise (IOCs) from article content"""
    
    # Regex patterns for different IOC types
    PATTERNS = {
        'ipv4': r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b',
        'ipv4_defanged': r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\[\.\]){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b',
        'ipv6': r'\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b',
        'domain': r'\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b',
        'domain_defanged': r'\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\[\.\])+[a-zA-Z]{2,}\b',
        'md5': r'\b[a-fA-F0-9]{32}\b',
        'sha1': r'\b[a-fA-F0-9]{40}\b',
        'sha256': r'\b[a-fA-F0-9]{64}\b',
        'cve': r'CVE-\d{4}-\d{4,7}',
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'email_defanged': r'\b[A-Za-z0-9._%+-]+\[@\][A-Za-z0-9.-]+\[\.\][A-Z|a-z]{2,}\b',
        'url': r'https?://[^\s<>"{}|\\^`\[\]]+',
        'url_defanged': r'hxxps?://[^\s<>"{}|\\^`]+',
    }
    
    # Common false positives to exclude
    FALSE_POSITIVES = {
        'ip': [
            '0.0.0.0', '127.0.0.1', '255.255.255.255',
            '192.168.1.1', '10.0.0.1', '172.16.0.1',
            '1.1.1.1', '8.8.8.8'  # Common DNS servers
        ],
        'domain': [
            'example.com', 'test.com', 'localhost', 'example.org',
            'test.org', 'sample.com', 'domain.com'
        ],
        'email': [
            'user@example.com', 'admin@example.com', 'test@test.com'
        ]
    }
    
    def __init__(self):
        self.compiled_patterns = {
            name: re.compile(pattern) 
            for name, pattern in self.PATTERNS.items()
        }
    
    @staticmethod
    def defang_to_normal(ioc: str) -> str:
        """Convert defanged IOC to normal format"""
        # Replace [.] with .
        ioc = ioc.replace('[.]', '.')
        # Replace [@] with @
        ioc = ioc.replace('[@]', '@')
        # Replace hxxp with http
        ioc = ioc.replace('hxxp://', 'http://').replace('hxxps://', 'https://')
        return ioc
    
    def extract_all(self, text: str) -> Dict[str, List[Dict]]:
        """Extract all IOCs from text with context (handles defanged notation)"""
        iocs = {
            'ips': [],
            'domains': [],
            'hashes': [],
            'cves': [],
            'emails': [],
            'urls': []
        }
        
        # Extract IPs (both normal and defanged IPv4)
        for match in self.compiled_patterns['ipv4'].finditer(text):
            ip = match.group()
            if self._validate_ip(ip):
                iocs['ips'].append({
                    'value': ip,
                    'type': 'ipv4',
                    'context': self._get_context(text, match.start(), match.end())
                })
        
        # Extract defanged IPs
        for match in self.compiled_patterns['ipv4_defanged'].finditer(text):
            ip_defanged = match.group()
            ip = self.defang_to_normal(ip_defanged)
            if self._validate_ip(ip):
                iocs['ips'].append({
                    'value': ip,
                    'type': 'ipv4',
                    'defanged': True,
                    'context': self._get_context(text, match.start(), match.end())
                })
        
        # Extract domains (normal)
        for match in self.compiled_patterns['domain'].finditer(text):
            domain = match.group()
            if self._validate_domain(domain):
                iocs['domains'].append({
                    'value': domain,
                    'context': self._get_context(text, match.start(), match.end())
                })
        
        # Extract defanged domains
        for match in self.compiled_patterns['domain_defanged'].finditer(text):
            domain_defanged = match.group()
            domain = self.defang_to_normal(domain_defanged)
            if self._validate_domain(domain):
                iocs['domains'].append({
                    'value': domain,
                    'defanged': True,
                    'context': self._get_context(text, match.start(), match.end())
                })
        
        # Extract hashes (MD5, SHA1, SHA256)
        for hash_type in ['md5', 'sha1', 'sha256']:
            for match in self.compiled_patterns[hash_type].finditer(text):
                hash_value = match.group()
                iocs['hashes'].append({
                    'value': hash_value,
                    'type': hash_type.upper(),
                    'context': self._get_context(text, match.start(), match.end())
                })
        
        # Extract CVEs
        for match in self.compiled_patterns['cve'].finditer(text):
            cve = match.group()
            iocs['cves'].append({
                'value': cve,
                'context': self._get_context(text, match.start(), match.end())
            })
        
        # Extract emails
        for match in self.compiled_patterns['email'].finditer(text):
            email = match.group()
            if self._validate_email(email):
                iocs['emails'].append({
                    'value': email,
                    'context': self._get_context(text, match.start(), match.end())
                })
        
        # Extract URLs
        for match in self.compiled_patterns['url'].finditer(text):
            url = match.group()
            iocs['urls'].append({
                'value': url,
                'context': self._get_context(text, match.start(), match.end())
            })
        
        # Remove duplicates
        for key in iocs:
            iocs[key] = self._deduplicate(iocs[key])
        
        return iocs
    
    def _get_context(self, text: str, start: int, end: int, window: int = 50) -> str:
        """Get surrounding context for an IOC"""
        context_start = max(0, start - window)
        context_end = min(len(text), end + window)
        return text[context_start:context_end].strip()
    
    def _validate_ip(self, ip: str) -> bool:
        """Validate IP address and filter false positives"""
        if ip in self.FALSE_POSITIVES['ip']:
            return False
        
        # Additional validation
        parts = ip.split('.')
        try:
            return all(0 <= int(part) <= 255 for part in parts)
        except ValueError:
            return False
    
    def _validate_domain(self, domain: str) -> bool:
        """Validate domain and filter false positives"""
        domain_lower = domain.lower()
        
        # Filter false positives
        if domain_lower in self.FALSE_POSITIVES['domain']:
            return False
        
        # Filter common file extensions that match domain pattern
        if domain_lower.endswith(('.jpg', '.png', '.gif', '.pdf', '.exe', '.dll')):
            return False
        
        # Must have at least one dot and valid TLD
        parts = domain_lower.split('.')
        if len(parts) < 2:
            return False
        
        # TLD should be 2+ characters
        if len(parts[-1]) < 2:
            return False
        
        return True
    
    def _validate_email(self, email: str) -> bool:
        """Validate email and filter false positives"""
        email_lower = email.lower()
        return email_lower not in self.FALSE_POSITIVES['email']
    
    def _deduplicate(self, ioc_list: List[Dict]) -> List[Dict]:
        """Remove duplicate IOCs while preserving first occurrence"""
        seen = set()
        unique = []
        for ioc in ioc_list:
            value = ioc['value'].lower()
            if value not in seen:
                seen.add(value)
                unique.append(ioc)
        return unique


# ============================================================================
# PHASE 1: KQL QUERY GENERATOR
# ============================================================================

class KQLQueryGenerator:
    """Generate KQL queries for threat hunting"""
    
    def __init__(self):
        self.extractor = IOCExtractor()
    
    def generate_queries(self, article: Dict) -> List[Dict]:
        """Generate all KQL queries for an article"""
        queries = []
        
        # Extract IOCs from article content
        iocs = self.extractor.extract_all(article.get('content', ''))
        
        # Generate queries based on extracted IOCs
        if iocs['ips']:
            queries.extend(self._generate_ip_queries(iocs['ips'], article))
        
        if iocs['domains']:
            queries.extend(self._generate_domain_queries(iocs['domains'], article))
        
        if iocs['hashes']:
            queries.extend(self._generate_hash_queries(iocs['hashes'], article))
        
        if iocs['cves']:
            queries.extend(self._generate_cve_queries(iocs['cves'], article))
        
        if iocs['urls']:
            queries.extend(self._generate_url_queries(iocs['urls'], article))
        
        return queries
    
    def _generate_ip_queries(self, ips: List[Dict], article: Dict) -> List[Dict]:
        """Generate queries for IP address hunting"""
        queries = []
        ip_list = [ip['value'] for ip in ips[:10]]  # Limit to 10 IPs
        
        if not ip_list:
            return queries
        
        ip_string = ', '.join(f"'{ip}'" for ip in ip_list)
        
        # Query 1: Network connections to malicious IPs
        queries.append({
            'name': f"Hunt for Malicious IPs from: {article['title'][:50]}",
            'type': 'IOC_Hunt',
            'category': 'Network',
            'platform': 'Microsoft Defender',
            'ioc_type': 'IP',
            'ioc_count': len(ip_list),
            'query': f"""// Hunt for network connections to malicious IPs
// Article: {article['title']}
// Risk: {article.get('threat_risk', 'N/A')}
DeviceNetworkEvents
| where Timestamp > ago(30d)
| where RemoteIP in ({ip_string})
| project Timestamp, DeviceName, RemoteIP, RemoteUrl, RemotePort, 
          InitiatingProcessFileName, InitiatingProcessCommandLine
| order by Timestamp desc""",
            'description': f"Hunt for network connections to {len(ip_list)} malicious IP(s) identified in the article.",
            'tables': ['DeviceNetworkEvents']
        })
        
        # Query 2: Firewall blocks
        queries.append({
            'name': f"Firewall Activity for Malicious IPs: {article['title'][:50]}",
            'type': 'IOC_Hunt',
            'category': 'Network',
            'platform': 'Microsoft Sentinel',
            'ioc_type': 'IP',
            'ioc_count': len(ip_list),
            'query': f"""// Check firewall activity for malicious IPs
// Article: {article['title']}
CommonSecurityLog
| where TimeGenerated > ago(30d)
| where DestinationIP in ({ip_string}) or SourceIP in ({ip_string})
| project TimeGenerated, SourceIP, DestinationIP, DeviceAction, 
          ApplicationProtocol, DestinationPort
| order by TimeGenerated desc""",
            'description': f"Check firewall logs for activity involving {len(ip_list)} malicious IP(s).",
            'tables': ['CommonSecurityLog']
        })
        
        return queries
    
    def _generate_domain_queries(self, domains: List[Dict], article: Dict) -> List[Dict]:
        """Generate queries for domain hunting"""
        queries = []
        domain_list = [d['value'] for d in domains[:10]]
        
        if not domain_list:
            return queries
        
        domain_string = ', '.join(f"'{domain}'" for domain in domain_list)
        
        # Query: DNS lookups
        queries.append({
            'name': f"Hunt for Malicious Domains: {article['title'][:50]}",
            'type': 'IOC_Hunt',
            'category': 'Network',
            'platform': 'Microsoft Defender',
            'ioc_type': 'Domain',
            'ioc_count': len(domain_list),
            'query': f"""// Hunt for DNS queries to malicious domains
// Article: {article['title']}
DeviceNetworkEvents
| where Timestamp > ago(30d)
| where RemoteUrl has_any ({domain_string})
| project Timestamp, DeviceName, RemoteUrl, RemoteIP, 
          InitiatingProcessFileName, InitiatingProcessCommandLine
| order by Timestamp desc""",
            'description': f"Hunt for DNS queries to {len(domain_list)} malicious domain(s).",
            'tables': ['DeviceNetworkEvents']
        })
        
        return queries
    
    def _generate_hash_queries(self, hashes: List[Dict], article: Dict) -> List[Dict]:
        """Generate queries for file hash hunting"""
        queries = []
        hash_list = [h['value'] for h in hashes[:10]]
        
        if not hash_list:
            return queries
        
        hash_string = ', '.join(f"'{h}'" for h in hash_list)
        
        # Query: File execution by hash
        queries.append({
            'name': f"Hunt for Malicious File Hashes: {article['title'][:50]}",
            'type': 'IOC_Hunt',
            'category': 'File',
            'platform': 'Microsoft Defender',
            'ioc_type': 'Hash',
            'ioc_count': len(hash_list),
            'query': f"""// Hunt for malicious file hashes
// Article: {article['title']}
DeviceFileEvents
| where Timestamp > ago(30d)
| where SHA256 in ({hash_string}) or SHA1 in ({hash_string}) or MD5 in ({hash_string})
| project Timestamp, DeviceName, FileName, FolderPath, SHA256, SHA1, MD5,
          InitiatingProcessFileName
| order by Timestamp desc""",
            'description': f"Hunt for {len(hash_list)} malicious file hash(es).",
            'tables': ['DeviceFileEvents']
        })
        
        return queries
    
    def _generate_cve_queries(self, cves: List[Dict], article: Dict) -> List[Dict]:
        """Generate queries for CVE hunting"""
        queries = []
        cve_list = [c['value'] for c in cves[:5]]
        
        if not cve_list:
            return queries
        
        cve_string = ', '.join(f"'{cve}'" for cve in cve_list)
        
        # Query: Vulnerability assessment logs
        queries.append({
            'name': f"Check for CVE Exposure: {article['title'][:50]}",
            'type': 'Vulnerability_Hunt',
            'category': 'Vulnerability',
            'platform': 'Microsoft Defender',
            'ioc_type': 'CVE',
            'ioc_count': len(cve_list),
            'query': f"""// Check for vulnerable software (CVEs)
// Article: {article['title']}
DeviceTvmSoftwareVulnerabilities
| where CveId in ({cve_string})
| summarize DeviceCount = dcount(DeviceId) by CveId, VulnerabilitySeverityLevel
| order by DeviceCount desc""",
            'description': f"Check for exposure to {len(cve_list)} CVE(s) mentioned in the article.",
            'tables': ['DeviceTvmSoftwareVulnerabilities']
        })
        
        return queries
    
    def _generate_url_queries(self, urls: List[Dict], article: Dict) -> List[Dict]:
        """Generate queries for URL hunting"""
        queries = []
        url_list = [u['value'] for u in urls[:10]]
        
        if not url_list:
            return queries
        
        url_string = ', '.join(f"'{url}'" for url in url_list)
        
        # Query: Web activity
        queries.append({
            'name': f"Hunt for Malicious URLs: {article['title'][:50]}",
            'type': 'IOC_Hunt',
            'category': 'Network',
            'platform': 'Microsoft Defender',
            'ioc_type': 'URL',
            'ioc_count': len(url_list),
            'query': f"""// Hunt for connections to malicious URLs
// Article: {article['title']}
DeviceNetworkEvents
| where Timestamp > ago(30d)
| where RemoteUrl in ({url_string})
| project Timestamp, DeviceName, RemoteUrl, RemoteIP,
          InitiatingProcessFileName, InitiatingProcessCommandLine
| order by Timestamp desc""",
            'description': f"Hunt for connections to {len(url_list)} malicious URL(s).",
            'tables': ['DeviceNetworkEvents']
        })
        
        return queries


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def extract_iocs_from_article(article: Dict) -> Dict:
    """Extract IOCs from a single article"""
    extractor = IOCExtractor()
    content = article.get('content', '')
    iocs = extractor.extract_all(content)
    
    # Add summary
    total = sum(len(iocs[key]) for key in iocs)
    log_info(f"Extracted {total} IOCs from '{article['title']}'")
    
    return iocs


def generate_kql_for_article(article: Dict) -> List[Dict]:
    """Generate KQL queries for a single article"""
    generator = KQLQueryGenerator()
    queries = generator.generate_queries(article)
    
    if queries:
        log_success(f"Generated {len(queries)} KQL queries for '{article['title']}'")
    else:
        log_warn(f"No queries generated for '{article['title']}' (no IOCs found)")
    
    return queries


def save_queries_to_file(queries: List[Dict], output_dir: str = "kql_queries") -> None:
    """Save queries to individual .kql files"""
    import os
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    for i, query in enumerate(queries, 1):
        # Create filename
        safe_name = re.sub(r'[^\w\s-]', '', query['name'])
        safe_name = re.sub(r'[-\s]+', '_', safe_name)
        filename = f"{i:02d}_{safe_name[:50]}.kql"
        filepath = os.path.join(output_dir, filename)
        
        # Write query to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(query['query'])
        
        log_success(f"Saved query to: {filepath}")


def generate_kql_batch(articles: List[Dict], export_dir: str = None) -> Dict:
    """
    Generate KQL queries for a batch of articles
    Returns summary statistics
    """
    generator = KQLQueryGenerator()
    all_queries = []
    stats = {
        'total_articles': len(articles),
        'articles_with_queries': 0,
        'total_queries': 0,
        'total_iocs': 0,
        'queries_by_type': {},
        'iocs_by_type': {}
    }
    
    for article in articles:
        queries = generator.generate_queries(article)
        
        if queries:
            stats['articles_with_queries'] += 1
            stats['total_queries'] += len(queries)
            
            # Count queries by type
            for query in queries:
                q_type = query['type']
                stats['queries_by_type'][q_type] = stats['queries_by_type'].get(q_type, 0) + 1
            
            all_queries.extend(queries)
        
        # Count IOCs
        iocs = generator.extractor.extract_all(article.get('content', ''))
        for ioc_type, ioc_list in iocs.items():
            if ioc_list:
                stats['total_iocs'] += len(ioc_list)
                stats['iocs_by_type'][ioc_type] = stats['iocs_by_type'].get(ioc_type, 0) + len(ioc_list)
    
    # Export queries if directory specified
    if export_dir and all_queries:
        save_queries_to_file(all_queries, export_dir)
    
    return all_queries, stats
