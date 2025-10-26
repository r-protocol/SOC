import sqlite3
from datetime import datetime, timedelta
from collections import defaultdict
import os

# Path to your database
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "threat_intel.db")

class ThreatIntelDB:
    def __init__(self, db_path=DATABASE_PATH):
        self.db_path = db_path
        print(f"📂 Using database: {os.path.abspath(self.db_path)}")
        
        # Verify database exists
        if not os.path.exists(self.db_path):
            print(f"❌ WARNING: Database not found at: {self.db_path}")
        else:
            print(f"✅ Database found!")
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _get_date_filter(self, days=None, start_date=None, end_date=None):
        """Helper to build date filter SQL"""
        if start_date and end_date:
            return f"published_date BETWEEN '{start_date}' AND '{end_date}'"
        elif days:
            date_threshold = (datetime.now() - timedelta(days=days)).isoformat()
            return f"published_date >= '{date_threshold}'"
        else:
            # Default to 7 days
            date_threshold = (datetime.now() - timedelta(days=7)).isoformat()
            return f"published_date >= '{date_threshold}'"
    
    def get_pipeline_overview(self, days=None, start_date=None, end_date=None):
        """Get pipeline statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            date_filter = self._get_date_filter(days, start_date, end_date)
            
            # Get total articles
            cursor.execute("SELECT COUNT(*) as total FROM articles")
            total_articles = cursor.fetchone()['total']
            
            # Get articles within date range
            cursor.execute(f"""
                SELECT COUNT(*) as recent 
                FROM articles 
                WHERE {date_filter}
            """)
            recent_articles = cursor.fetchone()['recent']
            
            # Get HIGH risk count within date range
            cursor.execute(f"""
                SELECT COUNT(*) as critical 
                FROM articles 
                WHERE threat_risk = 'HIGH' AND {date_filter}
            """)
            critical_count = cursor.fetchone()['critical']
            
            # Get total IOCs if iocs table exists
            try:
                cursor.execute("SELECT COUNT(*) as total FROM iocs")
                total_iocs = cursor.fetchone()['total']
            except:
                total_iocs = 0
            
            conn.close()
            
            return {
                "last_run": datetime.now().isoformat(),
                "articles_processed": total_articles,
                "filtered_items": recent_articles,
                "failed_runs": 0,
                "critical_threats": critical_count,
                "total_iocs": total_iocs
            }
        except Exception as e:
            print(f"❌ Error in get_pipeline_overview: {e}")
            conn.close()
            return {
                "last_run": datetime.now().isoformat(),
                "articles_processed": 0,
                "filtered_items": 0,
                "failed_runs": 0,
                "critical_threats": 0,
                "total_iocs": 0
            }
    
    def get_risk_distribution(self):
        """Get threat distribution by risk level"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT threat_risk, COUNT(*) as count
                FROM articles
                GROUP BY threat_risk
            """)
            
            data = {}
            for row in cursor.fetchall():
                if row['threat_risk']:
                    data[row['threat_risk']] = row['count']
            
            conn.close()
            return data
        except Exception as e:
            print(f"❌ Error in get_risk_distribution: {e}")
            conn.close()
            return {}
    
    def get_category_distribution(self, days=None, start_date=None, end_date=None):
        """Get threat distribution by category"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            date_filter = self._get_date_filter(days, start_date, end_date)
            
            cursor.execute(f"""
                SELECT category, COUNT(*) as count
                FROM articles
                WHERE category IS NOT NULL 
                AND category != 'Not Cybersecurity Related' 
                AND {date_filter}
                GROUP BY category
                ORDER BY count DESC
                LIMIT 10
            """)
            
            data = []
            for row in cursor.fetchall():
                data.append({
                    "name": row['category'],
                    "value": row['count']
                })
            
            conn.close()
            return data
        except Exception as e:
            print(f"❌ Error in get_category_distribution: {e}")
            conn.close()
            return []
    
    def get_threat_timeline(self, days=None, start_date=None, end_date=None):
        """Get threat counts over time"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            date_filter = self._get_date_filter(days, start_date, end_date)
            
            cursor.execute(f"""
                SELECT 
                    DATE(published_date) as date,
                    threat_risk,
                    COUNT(*) as count
                FROM articles
                WHERE {date_filter}
                AND category != 'Not Cybersecurity Related'
                AND threat_risk != 'NOT_RELEVANT'
                GROUP BY DATE(published_date), threat_risk
                ORDER BY date
            """)
            
            # Organize data by date and risk level
            timeline_data = defaultdict(lambda: {"HIGH": 0, "MEDIUM": 0, "LOW": 0})
            
            for row in cursor.fetchall():
                date = row['date']
                risk = row['threat_risk'] or 'LOW'
                timeline_data[date][risk] = row['count']
            
            # Convert to array format
            result = []
            for date in sorted(timeline_data.keys()):
                result.append({
                    "date": date,
                    "HIGH": timeline_data[date]["HIGH"],
                    "MEDIUM": timeline_data[date]["MEDIUM"],
                    "LOW": timeline_data[date]["LOW"]
                })
            
            conn.close()
            return result
        except Exception as e:
            print(f"❌ Error in get_threat_timeline: {e}")
            conn.close()
            return []
    
    def get_recent_threats(self, limit=10, risk_filter=None, days=None, start_date=None, end_date=None):
        """Get recent high-priority threats"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            date_filter = self._get_date_filter(days, start_date, end_date)
            
            query = f"""
                SELECT 
                    id, title, summary, category, threat_risk, 
                    published_date, url
                FROM articles
                WHERE {date_filter}
                AND category != 'Not Cybersecurity Related'
                AND threat_risk != 'NOT_RELEVANT'
            """
            
            if risk_filter:
                query += f" AND threat_risk = '{risk_filter}'"
            
            query += " ORDER BY published_date DESC LIMIT ?"
            
            cursor.execute(query, (limit,))
            
            threats = []
            for row in cursor.fetchall():
                # Get IOC count for this article
                ioc_count = 0
                try:
                    cursor.execute("SELECT COUNT(*) as count FROM iocs WHERE article_id = ?", (row['id'],))
                    ioc_result = cursor.fetchone()
                    if ioc_result:
                        ioc_count = ioc_result['count']
                except:
                    pass
                
                # Get KQL query count for this article
                kql_count = 0
                try:
                    cursor.execute("SELECT COUNT(*) as count FROM kql_queries WHERE article_id = ?", (row['id'],))
                    kql_result = cursor.fetchone()
                    if kql_result:
                        kql_count = kql_result['count']
                except:
                    pass
                
                threats.append({
                    "id": row['id'],
                    "title": row['title'],
                    "summary": row['summary'][:200] if row['summary'] else '',
                    "category": row['category'] or 'Uncategorized',
                    "risk_level": row['threat_risk'] or 'LOW',
                    "published_date": row['published_date'],
                    "source_url": row['url'],
                    "ioc_count": ioc_count,
                    "kql_count": kql_count
                })
            
            conn.close()
            return threats
        except Exception as e:
            print(f"❌ Error in get_recent_threats: {e}")
            conn.close()
            return []
    
    def get_ioc_stats(self):
        """Get IOC type breakdown"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT ioc_type, COUNT(*) as count
                FROM iocs
                GROUP BY ioc_type
            """)
            
            stats = {
                "domains": 0,
                "ips": 0,
                "hashes": 0,
                "cves": 0,
                "urls": 0,
                "emails": 0
            }
            
            for row in cursor.fetchall():
                ioc_type = row['ioc_type'].lower()
                count = row['count']
                
                if 'domain' in ioc_type:
                    stats["domains"] += count
                elif 'ip' in ioc_type:
                    stats["ips"] += count
                elif 'hash' in ioc_type or 'md5' in ioc_type or 'sha' in ioc_type:
                    stats["hashes"] += count
                elif 'cve' in ioc_type:
                    stats["cves"] += count
                elif 'url' in ioc_type:
                    stats["urls"] += count
                elif 'email' in ioc_type:
                    stats["emails"] += count
            
            conn.close()
            return stats
        except Exception as e:
            print(f"❌ Error in get_ioc_stats: {e}")
            conn.close()
            return {"domains": 0, "ips": 0, "hashes": 0, "cves": 0, "urls": 0, "emails": 0}
    
    def get_rss_feed_stats(self):
        """Get RSS feed statistics - Top 10 feeds by article count"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Extract domain from URL and count articles
            cursor.execute("""
                SELECT url, COUNT(*) as count
                FROM articles
                GROUP BY url
                ORDER BY count DESC
            """)
            
            # Build domain-based statistics
            source_counts = defaultdict(int)
            source_urls = defaultdict(str)
            
            for row in cursor.fetchall():
                url = row['url'] or ""
                count = row['count']
                
                # Extract domain/source name from URL
                domain = ""
                if "://" in url:
                    domain = url.split("://")[1].split("/")[0]
                else:
                    domain = url.split("/")[0]
                
                # Remove www. prefix
                domain = domain.replace("www.", "")
                
                source_counts[domain] += count
                if not source_urls[domain]:
                    source_urls[domain] = url
            
            # Get top 10 sources
            top_sources = sorted(source_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            
            feed_stats = []
            for domain, count in top_sources:
                # Clean up domain name for display
                display_name = domain.split('.')[0].title() if domain else "Unknown"
                
                # More readable names for known sources
                name_mapping = {
                    "bleepingcomputer": "BleepingComputer",
                    "thehackernews": "The Hacker News",
                    "darkreading": "Dark Reading",
                    "threatpost": "Threatpost",
                    "krebsonsecurity": "Krebs on Security",
                    "securityweek": "SecurityWeek",
                    "cyberscoop": "CyberScoop",
                    "zdnet": "ZDNet",
                    "arstechnica": "Ars Technica",
                    "theregister": "The Register"
                }
                
                for key, value in name_mapping.items():
                    if key in domain.lower():
                        display_name = value
                        break
                
                feed_stats.append({
                    "name": display_name,
                    "domain": domain,
                    "articles": count,
                    "parsed": count,
                    "last_success": datetime.now().isoformat()
                })
            
            conn.close()
            return feed_stats
        except Exception as e:
            print(f"❌ Error in get_rss_feed_stats: {e}")
            conn.close()
            return []
    
    def get_article_details(self, article_id):
        """Get detailed article information"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            print(f"🔍 Querying article {article_id} from database...")
            cursor.execute("""
                SELECT * FROM articles WHERE id = ?
            """, (article_id,))
            
            row = cursor.fetchone()
            
            if not row:
                print(f"⚠️ Article {article_id} not found in database")
                conn.close()
                return None
            
            print(f"✅ Article {article_id} found: {row['title'][:50]}...")
            
            # Get IOCs for this article
            iocs = []
            try:
                cursor.execute("""
                    SELECT ioc_type, ioc_value, context 
                    FROM iocs 
                    WHERE article_id = ?
                """, (article_id,))
                iocs = [dict(row) for row in cursor.fetchall()]
                print(f"📊 Found {len(iocs)} IOCs for article {article_id}")
            except Exception as ioc_err:
                print(f"⚠️ Error fetching IOCs: {ioc_err}")
                pass
            
            # Get KQL queries for this article
            kql_queries = []
            try:
                cursor.execute("""
                    SELECT query_name, kql_query, query_type, platform
                    FROM kql_queries
                    WHERE article_id = ?
                """, (article_id,))
                kql_queries = [dict(row) for row in cursor.fetchall()]
                print(f"📊 Found {len(kql_queries)} KQL queries for article {article_id}")
            except Exception as kql_err:
                print(f"⚠️ Error fetching KQL queries: {kql_err}")
                pass
            
            conn.close()
            
            # Access row fields properly
            content = row['content'] if 'content' in row.keys() else ''
            recommendations = row['recommendations'] if 'recommendations' in row.keys() else ''
            
            result = {
                "id": row['id'],
                "title": row['title'],
                "summary": row['summary'],
                "content": content,
                "category": row['category'],
                "risk_level": row['threat_risk'],
                "published_date": row['published_date'],
                "source_url": row['url'],
                "recommendations": recommendations,
                "iocs": iocs,
                "kql_queries": kql_queries
            }
            
            print(f"✅ Returning article data for {article_id}")
            return result
            
        except Exception as e:
            print(f"❌ Error in get_article_details for article {article_id}: {e}")
            import traceback
            traceback.print_exc()
            conn.close()
            return None
    
    def get_threat_families(self):
        """Extract threat family names for word cloud"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT category, title 
                FROM articles 
                WHERE category != 'Not Cybersecurity Related'
                AND threat_risk != 'NOT_RELEVANT'
            """)
            rows = cursor.fetchall()
            
            threat_names = defaultdict(int)
            keywords = ['Emotet', 'Qbot', 'TrickBot', 'Ransomware', 'Phishing', 
                       'Malware', 'APT', 'Lazarus', 'FIN7', 'Cobalt Strike',
                       'Conti', 'LockBit', 'BlackCat', 'REvil', 'DarkSide']
            
            for row in rows:
                text = (row['category'] or '') + ' ' + (row['title'] or '')
                for keyword in keywords:
                    if keyword.lower() in text.lower():
                        threat_names[keyword] += 1
            
            conn.close()
            
            return [{"text": name, "value": count} 
                    for name, count in threat_names.items() if count > 0]
        except Exception as e:
            print(f"❌ Error in get_threat_families: {e}")
            conn.close()
            return []

    def get_top_targeted_industries(self, limit=10, days=None, start_date=None, end_date=None):
        """Get top targeted industries from article content analysis"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            date_filter = self._get_date_filter(days, start_date, end_date)
            
            cursor.execute(f"""
                SELECT category, title, summary, content
                FROM articles
                WHERE category != 'Not Cybersecurity Related'
                AND threat_risk != 'NOT_RELEVANT'
                AND {date_filter}
            """)
            
            rows = cursor.fetchall()
            industry_counts = defaultdict(int)
            
            # Industry keywords mapping
            industry_keywords = {
                'Finance': ['bank', 'financial', 'finance', 'payment', 'credit', 'trading', 'fintech', 'cryptocurrency', 'crypto'],
                'Healthcare': ['health', 'hospital', 'medical', 'patient', 'healthcare', 'pharmaceutical', 'clinic'],
                'Government': ['government', 'federal', 'state', 'military', 'defense', 'agency', 'public sector'],
                'Manufacturing': ['manufacturing', 'industrial', 'factory', 'production', 'automotive', 'supply chain'],
                'Technology': ['tech', 'software', 'cloud', 'saas', 'it company', 'technology firm'],
                'Energy': ['energy', 'oil', 'gas', 'utility', 'power', 'electric', 'renewable'],
                'Retail': ['retail', 'ecommerce', 'e-commerce', 'shopping', 'store', 'consumer'],
                'Education': ['education', 'university', 'school', 'college', 'academic', 'student'],
                'Telecommunications': ['telecom', 'telecommunications', 'mobile', 'network provider', 'isp'],
                'Transportation': ['transportation', 'airline', 'shipping', 'logistics', 'aviation']
            }
            
            for row in rows:
                text = ' '.join([
                    row['category'] or '',
                    row['title'] or '',
                    row['summary'] or '',
                    row['content'] or ''
                ]).lower()
                
                for industry, keywords in industry_keywords.items():
                    if any(keyword in text for keyword in keywords):
                        industry_counts[industry] += 1
            
            conn.close()
            
            # Sort by count and return top N
            sorted_industries = sorted(industry_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
            return [{"name": industry, "value": count} for industry, count in sorted_industries]
            
        except Exception as e:
            print(f"❌ Error in get_top_targeted_industries: {e}")
            conn.close()
            return []

    def get_threat_actor_activity(self, limit=15, days=None, start_date=None, end_date=None):
        """Get threat actor activity from articles"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            date_filter = self._get_date_filter(days, start_date, end_date)
            
            cursor.execute(f"""
                SELECT id, title, category, published_date, summary
                FROM articles
                WHERE category != 'Not Cybersecurity Related'
                AND threat_risk != 'NOT_RELEVANT'
                AND {date_filter}
                ORDER BY published_date DESC
            """)
            
            rows = cursor.fetchall()
            actors = []
            
            # Known threat actors and groups with geographic coordinates
            threat_actors = {
                'Lazarus': {'country': 'North Korea', 'type': 'APT', 'lat': 40.3399, 'lon': 127.5101},
                'APT28': {'country': 'Russia', 'type': 'APT', 'lat': 61.5240, 'lon': 105.3188},
                'APT29': {'country': 'Russia', 'type': 'APT', 'lat': 61.5240, 'lon': 105.3188},
                'APT41': {'country': 'China', 'type': 'APT', 'lat': 35.8617, 'lon': 104.1954},
                'FIN7': {'country': 'Russia', 'type': 'Cybercrime', 'lat': 61.5240, 'lon': 105.3188},
                'Kimsuky': {'country': 'North Korea', 'type': 'APT', 'lat': 40.3399, 'lon': 127.5101},
                'Sandworm': {'country': 'Russia', 'type': 'APT', 'lat': 61.5240, 'lon': 105.3188},
                'Volt Typhoon': {'country': 'China', 'type': 'APT', 'lat': 35.8617, 'lon': 104.1954},
                'LockBit': {'country': 'Unknown', 'type': 'Ransomware', 'lat': 0, 'lon': 0},
                'Conti': {'country': 'Russia', 'type': 'Ransomware', 'lat': 61.5240, 'lon': 105.3188},
                'BlackCat': {'country': 'Unknown', 'type': 'Ransomware', 'lat': 0, 'lon': 0},
                'Cl0p': {'country': 'Russia', 'type': 'Ransomware', 'lat': 61.5240, 'lon': 105.3188},
                'REvil': {'country': 'Russia', 'type': 'Ransomware', 'lat': 61.5240, 'lon': 105.3188},
                'Scattered Spider': {'country': 'Unknown', 'type': 'Cybercrime', 'lat': 0, 'lon': 0},
                'TA505': {'country': 'Russia', 'type': 'Cybercrime', 'lat': 61.5240, 'lon': 105.3188},
                'APT32': {'country': 'Vietnam', 'type': 'APT', 'lat': 14.0583, 'lon': 108.2772},
                'APT33': {'country': 'Iran', 'type': 'APT', 'lat': 32.4279, 'lon': 53.6880},
                'APT34': {'country': 'Iran', 'type': 'APT', 'lat': 32.4279, 'lon': 53.6880},
                'APT37': {'country': 'North Korea', 'type': 'APT', 'lat': 40.3399, 'lon': 127.5101},
                'APT38': {'country': 'North Korea', 'type': 'APT', 'lat': 40.3399, 'lon': 127.5101},
                'APT39': {'country': 'Iran', 'type': 'APT', 'lat': 32.4279, 'lon': 53.6880},
                'Storm-0978': {'country': 'China', 'type': 'APT', 'lat': 35.8617, 'lon': 104.1954},
                'Mustang Panda': {'country': 'China', 'type': 'APT', 'lat': 35.8617, 'lon': 104.1954}
            }
            
            for row in rows:
                text = (row['title'] + ' ' + (row['summary'] or '')).lower()
                
                for actor, info in threat_actors.items():
                    if actor.lower() in text:
                        actors.append({
                            'actor': actor,
                            'country': info['country'],
                            'type': info['type'],
                            'lat': info['lat'],
                            'lon': info['lon'],
                            'article_title': row['title'],
                            'date': row['published_date'],
                            'article_id': row['id']
                        })
                        break  # Only count once per article
            
            conn.close()
            return actors[:limit]
            
        except Exception as e:
            print(f"❌ Error in get_threat_actor_activity: {e}")
            conn.close()
            return []

    def get_attack_vectors(self, days=None, start_date=None, end_date=None):
        """Get attack vector distribution from articles"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            date_filter = self._get_date_filter(days, start_date, end_date)
            
            cursor.execute(f"""
                SELECT title, summary, content, category
                FROM articles
                WHERE category != 'Not Cybersecurity Related'
                AND threat_risk != 'NOT_RELEVANT'
                AND {date_filter}
            """)
            
            rows = cursor.fetchall()
            vector_counts = defaultdict(int)
            
            # Attack vector keywords
            vectors = {
                'Phishing': ['phishing', 'spear phishing', 'email attack', 'credential theft', 'fake email'],
                'Exploit': ['exploit', 'vulnerability', 'cve', 'zero-day', '0-day', 'rce', 'remote code execution'],
                'Malware': ['malware', 'trojan', 'rat', 'backdoor', 'dropper', 'loader'],
                'Ransomware': ['ransomware', 'encryption', 'ransom', 'extortion'],
                'Supply Chain': ['supply chain', 'third-party', 'vendor compromise', 'software supply'],
                'Credential Access': ['credential', 'password', 'stolen credentials', 'brute force', 'password spray'],
                'Web Application': ['web attack', 'sql injection', 'xss', 'web shell', 'web application'],
                'Social Engineering': ['social engineering', 'pretexting', 'baiting', 'quid pro quo'],
                'DDoS': ['ddos', 'denial of service', 'distributed denial'],
                'Insider Threat': ['insider', 'insider threat', 'malicious insider']
            }
            
            for row in rows:
                text = ' '.join([
                    row['title'] or '',
                    row['summary'] or '',
                    row['content'] or '',
                    row['category'] or ''
                ]).lower()
                
                for vector, keywords in vectors.items():
                    if any(keyword in text for keyword in keywords):
                        vector_counts[vector] += 1
            
            conn.close()
            
            # Sort by count
            sorted_vectors = sorted(vector_counts.items(), key=lambda x: x[1], reverse=True)
            return [{"name": vector, "value": count} for vector, count in sorted_vectors if count > 0]
            
        except Exception as e:
            print(f"❌ Error in get_attack_vectors: {e}")
            conn.close()
            return []

    def get_trending_cves(self, limit=10, days=None, start_date=None, end_date=None):
        """Get trending CVEs from IOCs and articles"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            date_filter = self._get_date_filter(days, start_date, end_date)
            
            # Get CVEs from IOCs table
            cursor.execute(f"""
                SELECT i.ioc_value, i.context, a.title, a.published_date, a.threat_risk, a.id
                FROM iocs i
                JOIN articles a ON i.article_id = a.id
                WHERE i.ioc_type = 'cves'
                AND a.category != 'Not Cybersecurity Related'
                AND a.threat_risk != 'NOT_RELEVANT'
                AND a.{date_filter}
                ORDER BY a.published_date DESC
            """)
            
            cve_data = defaultdict(lambda: {'count': 0, 'articles': [], 'severity': 'UNKNOWN', 'context': []})
            
            for row in cursor.fetchall():
                cve = row['ioc_value']
                cve_data[cve]['count'] += 1
                cve_data[cve]['articles'].append({
                    'title': row['title'],
                    'date': row['published_date'],
                    'id': row['id']
                })
                
                # Determine severity from article risk
                if row['threat_risk'] == 'HIGH':
                    cve_data[cve]['severity'] = 'CRITICAL'
                elif cve_data[cve]['severity'] == 'UNKNOWN' and row['threat_risk'] == 'MEDIUM':
                    cve_data[cve]['severity'] = 'HIGH'
                
                if row['context']:
                    cve_data[cve]['context'].append(row['context'])
            
            # Convert to list and sort by count
            cves = []
            for cve, data in cve_data.items():
                cves.append({
                    'cve': cve,
                    'count': data['count'],
                    'severity': data['severity'],
                    'latest_article': data['articles'][0]['title'] if data['articles'] else '',
                    'date': data['articles'][0]['date'] if data['articles'] else '',
                    'context': data['context'][0] if data['context'] else ''
                })
            
            cves.sort(key=lambda x: x['count'], reverse=True)
            conn.close()
            
            return cves[:limit]
            
        except Exception as e:
            print(f"❌ Error in get_trending_cves: {e}")
            import traceback
            traceback.print_exc()
            conn.close()
            return []

