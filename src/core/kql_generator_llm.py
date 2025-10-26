# kql_generator_llm.py
"""
LLM-Enhanced KQL Query Generator for Threat Intelligence
Uses Ollama LLM to intelligently extract IOCs and generate context-aware KQL queries
"""

import requests
import json
import re
from typing import Dict, List, Optional
from src.config import OLLAMA_MODEL, OLLAMA_HOST
from src.utils.logging_utils import log_info, log_success, log_warn, log_error, BColors

# Import regex-based extractor as fallback
from src.core.kql_generator import IOCExtractor as RegexIOCExtractor, KQLQueryGenerator as TemplateGenerator


class LLMKQLGenerator:
    """Generate KQL queries using LLM for intelligent IOC extraction and query generation"""
    
    def __init__(self):
        self.regex_extractor = RegexIOCExtractor()  # Fallback
        self.template_generator = TemplateGenerator()  # Fallback
    
    def extract_iocs_with_llm(self, article: Dict) -> Dict:
        """Use LLM to extract IOCs with context understanding"""
        
        prompt = f"""You are a cybersecurity threat intelligence analyst. Extract ONLY real Indicators of Compromise (IOCs) that are explicitly mentioned in the article text.

CRITICAL RULES:
1. Output ONLY valid JSON. No markdown, no explanations.
2. Extract ONLY IOCs that appear in the article content
3. DO NOT generate example IPs like 192.168.x.x or 203.0.113.x (these are private/documentation IPs)
4. DO NOT invent or hallucinate IOCs
5. If no IOCs are found, return empty arrays

Extract and categorize IOCs into these types:
1. **ips**: IPv4/IPv6 addresses (PUBLIC IPs only, not 10.x, 172.16-31.x, 192.168.x)
2. **domains**: Domain names (include defanged like evil[.]com)
3. **urls**: Full URLs (include defanged)
4. **hashes**: File hashes (MD5, SHA1, SHA256, SHA512)
5. **cves**: CVE identifiers (CVE-YYYY-NNNNN format)
6. **emails**: Email addresses
7. **filenames**: Malicious filenames mentioned
8. **registry_keys**: Windows registry keys
9. **techniques**: MITRE ATT&CK technique IDs (T1234 format)

For each IOC, include:
- "value": the IOC (normalize defanged: evil[.]com → evil.com)
- "context": "attacker" or "victim" or "infrastructure" 
- "confidence": "high" (explicitly stated), "medium" (implied), or "low" (mentioned casually)
- "description": brief context from article

Article Title: {article['title']}
Article Content: {article.get('content', '')[:6000]}

Output JSON structure:
{{
  "ips": [],
  "domains": [],
  "urls": [],
  "hashes": [],
  "cves": [],
  "emails": [],
  "filenames": [],
  "registry_keys": [],
  "techniques": []
}}

Respond with JSON only:"""

        try:
            response = requests.post(
                f"{OLLAMA_HOST}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,  # Very low for better JSON structure
                        "top_p": 0.9,
                        "num_predict": 16384  # Allow very long responses for many IOCs (98 domains)
                    }
                },
                timeout=120
            )
            response.raise_for_status()
            response_text = response.json()['response'].strip()
            
            # Parse JSON
            iocs = self._parse_llm_response(response_text)
            
            if iocs:
                total = sum(len(iocs.get(key, [])) for key in iocs)
                log_success(f"LLM extracted {total} IOCs from '{article['title']}'")
                return iocs
            else:
                log_warn(f"LLM returned empty IOCs, falling back to regex for '{article['title']}'")
                return self._fallback_extraction(article)
                
        except Exception as e:
            log_error(f"LLM extraction failed: {e}, using regex fallback")
            return self._fallback_extraction(article)
    
    def _parse_llm_response(self, response_text: str) -> Optional[Dict]:
        """Parse LLM JSON response with repair"""
        # Find JSON boundaries
        json_start = response_text.find('{')
        json_end = response_text.rfind('}')
        
        if json_start == -1 or json_end == -1:
            return None
        
        json_str = response_text[json_start:json_end + 1]
        
        try:
            iocs = json.loads(json_str)
            
            # Validate structure
            expected_keys = ['ips', 'domains', 'urls', 'hashes', 'cves', 'emails']
            if not any(key in iocs for key in expected_keys):
                log_warn("LLM response missing expected IOC categories")
                return None
            
            # Ensure all lists exist
            for key in expected_keys + ['filenames', 'registry_keys', 'techniques']:
                if key not in iocs:
                    iocs[key] = []
            
            return iocs
            
        except json.JSONDecodeError as e:
            log_error(f"Failed to parse LLM JSON: {e}")
            return None
    
    def _fallback_extraction(self, article: Dict) -> Dict:
        """Fallback to regex-based extraction"""
        log_info(f"Using regex fallback for '{article['title']}'")
        regex_iocs = self.regex_extractor.extract_all(article.get('content', ''))
        
        # Convert regex format to LLM format
        enhanced_iocs = {
            'ips': [{'value': ioc['value'], 'context': 'unknown', 'confidence': 'medium', 'description': ioc.get('context', '')} 
                    for ioc in regex_iocs.get('ips', [])],
            'domains': [{'value': ioc['value'], 'context': 'unknown', 'confidence': 'medium', 'description': ioc.get('context', '')} 
                        for ioc in regex_iocs.get('domains', [])],
            'urls': [{'value': ioc['value'], 'context': 'unknown', 'confidence': 'medium', 'description': ioc.get('context', '')} 
                     for ioc in regex_iocs.get('urls', [])],
            'hashes': [{'value': ioc['value'], 'context': 'unknown', 'confidence': 'medium', 'description': ioc.get('context', '')} 
                       for ioc in regex_iocs.get('hashes', [])],
            'cves': [{'value': ioc['value'], 'context': 'unknown', 'confidence': 'high', 'description': ioc.get('context', '')} 
                     for ioc in regex_iocs.get('cves', [])],
            'emails': [{'value': ioc['value'], 'context': 'unknown', 'confidence': 'medium', 'description': ioc.get('context', '')} 
                       for ioc in regex_iocs.get('emails', [])],
            'filenames': [],
            'registry_keys': [],
            'techniques': []
        }
        
        return enhanced_iocs
    
    def generate_kql_with_llm(self, article: Dict, iocs: Dict) -> List[Dict]:
        """Use LLM to generate context-aware KQL queries"""
        
        # Filter high-confidence IOCs for query generation
        high_conf_iocs = self._filter_high_confidence(iocs)
        
        # Validate IOCs - remove hallucinated/private IPs
        high_conf_iocs = self._validate_iocs(high_conf_iocs)
        
        # If no real IOCs, try to generate behavioral/TTP-based queries
        if not high_conf_iocs:
            log_info(f"No IOCs found in '{article['title']}', analyzing for behavioral hunting queries")
            return self._generate_behavioral_queries(article)
        
        # Determine primary IOC type
        ioc_counts = {k: len(v) for k, v in high_conf_iocs.items() if v}
        primary_type = max(ioc_counts, key=ioc_counts.get) if ioc_counts else 'domains'
        ioc_count = ioc_counts.get(primary_type, 0)
        
        # Limit IOCs in prompt to avoid huge prompts
        limited_iocs = {}
        for ioc_type, ioc_list in high_conf_iocs.items():
            if len(ioc_list) > 10:
                limited_iocs[ioc_type] = ioc_list[:10] + [{'value': f'... and {len(ioc_list)-10} more {ioc_type}'}]
            else:
                limited_iocs[ioc_type] = ioc_list
        
        prompt = f"""You are a threat hunting expert. Generate ONE focused, comprehensive KQL query for Microsoft Defender/Sentinel.

Article: {article['title']}
Risk: {article.get('threat_risk', 'UNKNOWN')}
Category: {article.get('category', 'Unknown')}

Primary IOC Type: {primary_type.upper()} ({ioc_count} total)
Sample IOCs:
{json.dumps(limited_iocs, indent=2)}

TASK: Generate ONE comprehensive query that focuses on the primary IOC type ({primary_type}).

For DOMAINS: Hunt for network connections, DNS queries, and firewall logs
For IPS: Hunt for network connections and firewall blocks
For HASHES: Hunt for file creations and process executions
For CVES: Hunt for vulnerable software and exploitation attempts

Provide:
1. **name**: Specific, descriptive query name related to the article
2. **type**: "IOC_Hunt"
3. **description**: What the query detects (be specific)
4. **kql**: ONE comprehensive query that:
   - Uses appropriate tables (DeviceNetworkEvents, DnsEvents, CommonSecurityLog, etc.)
   - Includes ALL IOC values using has_any() for lists
   - Has time filter ago(30d)
   - Aggregates results (summarize by device)
   - Projects relevant fields
   - Has clear comments

IMPORTANT:
- Generate ONLY ONE query (the most effective one)
- Include ALL {ioc_count} IOCs in the query (use has_any or in operators)
- Use proper KQL syntax
- Add helpful comments

Output JSON only:
{{
  "queries": [
    {{
      "name": "Hunt for Conti Ransomware Domain Connections",
      "type": "IOC_Hunt",
      "description": "Detect network connections to Conti ransomware C2 domains",
      "platform": "Microsoft Defender",
      "kql": "// Hunt for connections to Conti domains\\nDeviceNetworkEvents\\n| where Timestamp > ago(30d)\\n| where RemoteUrl has_any ('domain1.com', 'domain2.com')\\n| summarize FirstSeen=min(Timestamp), LastSeen=max(Timestamp), Count=count() by DeviceName, RemoteUrl"
    }}
  ]
}}

Respond with JSON only:"""

        try:
            response = requests.post(
                f"{OLLAMA_HOST}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,  # Very low for structured JSON output
                        "top_p": 0.9,
                        "num_predict": 4096
                    }
                },
                timeout=120
            )
            response.raise_for_status()
            response_text = response.json()['response'].strip()
            
            # Parse queries
            queries = self._parse_query_response(response_text, article)
            
            if queries:
                # Inject actual IOCs into the query
                queries = self._inject_iocs_into_queries(queries, high_conf_iocs)
                log_success(f"LLM generated {len(queries)} focused query for '{article['title']}'")
                return queries
            else:
                log_warn(f"LLM query generation failed, using templates for '{article['title']}'")
                return self.template_generator.generate_queries(article)
                
        except Exception as e:
            log_error(f"LLM query generation failed: {e}, using templates")
            return self.template_generator.generate_queries(article)
    
    def _inject_iocs_into_queries(self, queries: List[Dict], iocs: Dict) -> List[Dict]:
        """Inject actual IOC values into the generated queries"""
        for query in queries:
            if 'query' not in query:
                continue
            
            kql = query['query']
            
            # Determine primary IOC type from the query
            if 'domains' in iocs and len(iocs['domains']) > 0:
                # Build domain list for has_any
                domain_values = [ioc['value'] for ioc in iocs['domains'] if isinstance(ioc, dict)]
                if domain_values:
                    # Format as KQL list
                    domains_str = ', '.join([f'"{d}"' for d in domain_values])
                    # Replace placeholder or inject into where clause
                    if 'has_any' in kql or 'RemoteUrl' in kql:
                        # Find and replace the has_any list
                        import re
                        kql = re.sub(r"has_any\s*\([^)]+\)", f"has_any ({domains_str})", kql)
                    query['query'] = kql
                    query['ioc_count'] = len(domain_values)
            
            elif 'ips' in iocs and len(iocs['ips']) > 0:
                # Build IP list
                ip_values = [ioc['value'] for ioc in iocs['ips'] if isinstance(ioc, dict)]
                if ip_values:
                    ips_str = ', '.join([f'"{ip}"' for ip in ip_values])
                    import re
                    kql = re.sub(r"in\s*\([^)]+\)", f"in ({ips_str})", kql)
                    query['query'] = kql
                    query['ioc_count'] = len(ip_values)
            
            elif 'hashes' in iocs and len(iocs['hashes']) > 0:
                # Build hash list
                hash_values = [ioc['value'] for ioc in iocs['hashes'] if isinstance(ioc, dict)]
                if hash_values:
                    hashes_str = ', '.join([f'"{h}"' for h in hash_values])
                    import re
                    kql = re.sub(r"in\s*\([^)]+\)", f"in ({hashes_str})", kql)
                    query['query'] = kql
                    query['ioc_count'] = len(hash_values)
        
        return queries
    
    def _validate_iocs(self, iocs: Dict) -> Dict:
        """Remove hallucinated or invalid IOCs"""
        import ipaddress
        
        validated = {}
        
        # Validate IPs - remove private/reserved IPs
        if 'ips' in iocs and iocs['ips']:
            valid_ips = []
            for ioc in iocs['ips']:
                if isinstance(ioc, dict):
                    ip = ioc.get('value', '')
                    try:
                        ip_obj = ipaddress.ip_address(ip)
                        # Skip private, loopback, reserved IPs
                        if not (ip_obj.is_private or ip_obj.is_loopback or 
                               ip_obj.is_reserved or ip_obj.is_multicast):
                            # Skip common placeholders
                            if ip not in ['203.0.113.1', '203.0.113.0', '198.51.100.1']:
                                valid_ips.append(ioc)
                    except:
                        pass
            if valid_ips:
                validated['ips'] = valid_ips
        
        # Validate domains - remove example domains
        if 'domains' in iocs and iocs['domains']:
            valid_domains = []
            invalid_domains = ['example.com', 'example.org', 'example.net', 'test.com', 'domain.com']
            for ioc in iocs['domains']:
                if isinstance(ioc, dict):
                    domain = ioc.get('value', '').lower()
                    if domain and domain not in invalid_domains and not domain.startswith('example'):
                        valid_domains.append(ioc)
            if valid_domains:
                validated['domains'] = valid_domains
        
        # Pass through other IOC types (hashes, CVEs are usually real)
        for ioc_type in ['hashes', 'cves', 'urls', 'emails']:
            if ioc_type in iocs and iocs[ioc_type]:
                validated[ioc_type] = iocs[ioc_type]
        
        return validated
    
    def _generate_behavioral_queries(self, article: Dict) -> List[Dict]:
        """Generate TTP-based hunting queries when no IOCs are available"""
        
        prompt = f"""You are a threat hunting expert. Analyze this cybersecurity article and generate ONE behavioral/TTP-based KQL hunting query.

Article: {article['title']}
Category: {article.get('category', 'Unknown')}
Risk: {article.get('threat_risk', 'UNKNOWN')}
Summary: {article.get('summary', '')}
Content: {article.get('content', '')[:3000]}

TASK: If this article describes a real threat (malware, attack technique, vulnerability exploitation):
1. Understand the threat's behavior and TTPs
2. Generate ONE behavioral KQL query that hunts for signs of this threat
3. Focus on: suspicious processes, registry changes, file operations, network patterns, command patterns

If this is just news/awareness/policy content (no technical threat):
- Return empty response

For behavioral queries, focus on:
- Process execution patterns (suspicious command lines, parent-child relationships)
- File operations (unusual file writes, extensions, paths)
- Registry modifications (persistence mechanisms)
- Network behavior (connection patterns, protocols, ports)
- Authentication anomalies (failed logins, privilege escalation)

Use tables like:
- DeviceProcessEvents (process creation, command lines)
- DeviceFileEvents (file operations)
- DeviceRegistryEvents (registry changes)
- DeviceNetworkEvents (network connections)
- SecurityEvent (authentication, privileges)

Output JSON:
{{
  "name": "Descriptive query name based on threat behavior",
  "type": "Behavioral_Hunt",
  "description": "What this query detects (be specific to the threat)",
  "tables": ["DeviceProcessEvents", "DeviceFileEvents"],
  "mitre_techniques": ["T1059", "T1055"],
  "query": "// KQL query here\\nDeviceProcessEvents\\n| where..."
}}

Return ONLY JSON. If not a technical threat, return: {{"skip": true}}
"""

        try:
            response = requests.post(
                f"{OLLAMA_HOST}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.2,  # Slightly higher for creative behavioral queries
                        "top_p": 0.9,
                        "num_predict": 2048
                    }
                },
                timeout=120
            )
            response.raise_for_status()
            response_text = response.json()['response'].strip()
            
            # Parse response - look for JSON
            json_start = response_text.find('{')
            json_end = response_text.rfind('}')
            
            if json_start == -1 or json_end == -1:
                log_info(f"No JSON response for '{article['title']}', skipping")
                return []
            
            json_str = response_text[json_start:json_end + 1]
            
            try:
                query_data = json.loads(json_str)
            except json.JSONDecodeError as e:
                log_error(f"Failed to parse behavioral query JSON: {e}")
                return []
            
            if not query_data or query_data.get('skip'):
                log_info(f"Article '{article['title']}' is not technical threat content, skipping")
                return []
            
            # Format as query list
            query = {
                'name': query_data.get('name', 'Behavioral Hunt'),
                'type': query_data.get('type', 'Behavioral_Hunt'),
                'description': query_data.get('description', 'Hunt for threat behavior'),
                'query': query_data.get('query', ''),
                'tables': query_data.get('tables', []),
                'mitre_techniques': query_data.get('mitre_techniques', []),
                'platform': 'Microsoft Defender',
                'ioc_count': 0  # No IOCs, behavioral only
            }
            
            log_success(f"Generated behavioral hunting query for '{article['title']}'")
            return [query]
            
        except Exception as e:
            log_error(f"Failed to generate behavioral query: {e}")
            return []
    
    def _filter_high_confidence(self, iocs: Dict) -> Dict:
        """Filter IOCs by confidence level"""
        filtered = {}
        
        for ioc_type, ioc_list in iocs.items():
            if isinstance(ioc_list, list):
                high_conf = [
                    ioc for ioc in ioc_list 
                    if isinstance(ioc, dict) and ioc.get('confidence', 'low') in ['high', 'medium']
                ]
                if high_conf:
                    filtered[ioc_type] = high_conf
        
        return filtered
    
    def _parse_query_response(self, response_text: str, article: Dict) -> List[Dict]:
        """Parse LLM query response"""
        json_start = response_text.find('{')
        json_end = response_text.rfind('}')
        
        if json_start == -1 or json_end == -1:
            return []
        
        json_str = response_text[json_start:json_end + 1]
        
        try:
            parsed = json.loads(json_str)
            queries = parsed.get('queries', [])
            
            # Enhance query metadata
            for query in queries:
                query['article_title'] = article['title']
                query['threat_risk'] = article.get('threat_risk', 'UNKNOWN')
                
                # Clean up KQL (unescape newlines)
                if 'kql' in query:
                    query['query'] = query['kql'].replace('\\n', '\n')
                    del query['kql']
                
                # Add defaults
                if 'platform' not in query:
                    query['platform'] = 'Microsoft Defender'
                if 'category' not in query:
                    query['category'] = 'Network'
                if 'tables' not in query:
                    query['tables'] = self._extract_tables(query.get('query', ''))
            
            return queries
            
        except json.JSONDecodeError as e:
            log_error(f"Failed to parse query JSON: {e}")
            return []
    
    def _extract_tables(self, kql: str) -> List[str]:
        """Extract table names from KQL query"""
        tables = []
        # Common Defender/Sentinel tables
        table_patterns = [
            'DeviceNetworkEvents', 'DeviceFileEvents', 'DeviceProcessEvents',
            'DeviceLogonEvents', 'DeviceEvents', 'DeviceRegistryEvents',
            'CommonSecurityLog', 'SecurityEvent', 'Syslog',
            'EmailEvents', 'EmailAttachmentInfo', 'DeviceTvmSoftwareVulnerabilities'
        ]
        
        for table in table_patterns:
            if table in kql:
                tables.append(table)
        
        return tables
    
    def generate_all(self, article: Dict) -> tuple:
        """
        Full LLM-based generation pipeline
        Returns: (iocs, queries)
        """
        # Step 1: Extract IOCs with LLM
        iocs = self.extract_iocs_with_llm(article)
        
        # Step 2: Generate queries with LLM
        queries = self.generate_kql_with_llm(article, iocs)
        
        return iocs, queries


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def generate_kql_llm(article: Dict) -> tuple:
    """
    Main function to generate IOCs and KQL queries using LLM
    Returns: (iocs, queries)
    """
    generator = LLMKQLGenerator()
    iocs, queries = generator.generate_all(article)
    
    total_iocs = sum(len(iocs.get(key, [])) for key in iocs)
    log_info(f"Total: {total_iocs} IOCs, {len(queries)} queries for '{article['title']}'")
    
    return iocs, queries


def generate_kql_batch_llm(articles: List[Dict]) -> tuple:
    """
    Generate KQL for multiple articles using LLM
    Returns: (all_iocs_dict, all_queries_list)
    """
    generator = LLMKQLGenerator()
    all_iocs = {}
    all_queries = []
    
    for article in articles:
        iocs, queries = generator.generate_all(article)
        all_iocs[article['title']] = iocs
        all_queries.extend(queries)
    
    return all_iocs, all_queries


if __name__ == "__main__":
    # Test with sample article
    print(f"\n{BColors.HEADER}=== LLM KQL Generator Test ==={BColors.ENDC}\n")
    
    test_article = {
        'title': 'New Ransomware Campaign Targets Healthcare',
        'content': '''
        A sophisticated ransomware campaign has been targeting healthcare organizations.
        The attackers use IP address 192[.]168[.]100[.]50 as their command and control server.
        They also operate backup infrastructure at evil-domain[.]com and malicious-site[.]net.
        
        The malware file hash is SHA256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
        
        This campaign exploits CVE-2024-1234 to gain initial access.
        Phishing emails from attacker@evil[.]com are used as the initial vector.
        ''',
        'threat_risk': 'HIGH',
        'category': 'Ransomware'
    }
    
    iocs, queries = generate_kql_llm(test_article)
    
    print(f"\n{BColors.OKCYAN}IOCs Extracted:{BColors.ENDC}")
    for ioc_type, ioc_list in iocs.items():
        if ioc_list:
            print(f"  {ioc_type}: {len(ioc_list)}")
            for ioc in ioc_list[:2]:
                if isinstance(ioc, dict):
                    print(f"    - {ioc.get('value')} (confidence: {ioc.get('confidence')})")
    
    print(f"\n{BColors.OKCYAN}KQL Queries Generated:{BColors.ENDC}")
    for i, query in enumerate(queries, 1):
        print(f"\n{BColors.OKGREEN}Query {i}: {query.get('name')}{BColors.ENDC}")
        print(f"  Type: {query.get('type')}")
        print(f"  Platform: {query.get('platform')}")
        print(f"  Description: {query.get('description')}")
        if 'query' in query:
            print(f"  Query preview: {query['query'][:100]}...")
    
    print(f"\n{BColors.HEADER}=== Test Complete! ==={BColors.ENDC}\n")
