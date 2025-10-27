import sqlite3
from datetime import datetime, timedelta
from collections import defaultdict
import os
import re

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

    @staticmethod
    def _cvss_to_severity(score: float) -> str:
        """Map CVSS base score (0.0-10.0) to severity label.
        Low: 0.1–3.9, Medium: 4.0–6.9, High: 7.0–8.9, Critical: 9.0–10.0, 0.0 => LOW.
        """
        try:
            s = float(score)
        except Exception:
            return 'UNKNOWN'
        if s <= 0:
            return 'LOW'
        if 0.0 < s <= 3.9:
            return 'LOW'
        if 4.0 <= s <= 6.9:
            return 'MEDIUM'
        if 7.0 <= s <= 8.9:
            return 'HIGH'
        if 9.0 <= s <= 10.0:
            return 'CRITICAL'
        return 'UNKNOWN'

    @staticmethod
    def _extract_cvss_score(text: str):
        """Best-effort CVSS score extraction from arbitrary text/context.
        Looks for patterns like 'CVSS 9.8', 'CVSS v3.1 Base Score: 8.6', or 'Base score 7.5'.
        Returns float or None if not found.
        """
        if not text:
            return None
        patterns = [
            r"CVSS\s*(?:v?[23](?:\.[01])?)?\s*(?:Base\s*Score:?)?\s*([0-9]{1,2}(?:\.[0-9])?)",
            r"Base\s*Score\s*:?\s*([0-9]{1,2}(?:\.[0-9])?)",
            r"CVSS\s*Score\s*:?\s*([0-9]{1,2}(?:\.[0-9])?)",
        ]
        for pat in patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                try:
                    val = float(m.group(1))
                    if 0.0 <= val <= 10.0:
                        return val
                except Exception:
                    continue
        return None
    
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
            
            # Get total KQL queries if kql_queries table exists
            try:
                cursor.execute("SELECT COUNT(*) as total FROM kql_queries")
                total_kql = cursor.fetchone()['total']
            except:
                total_kql = 0
            
            conn.close()
            
            return {
                "last_run": datetime.now().isoformat(),
                "articles_processed": total_articles,
                "filtered_items": recent_articles,
                "failed_runs": 0,
                "critical_threats": critical_count,
                "total_iocs": total_iocs,
                "total_kql": total_kql
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
                "total_iocs": 0,
                "total_kql": 0
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
                AND category != 'Pending Analysis'
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

    def get_threat_actor_activity(self, limit=50, days=None, start_date=None, end_date=None):
        """Get threat actor activity dynamically extracted from articles"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            date_filter = self._get_date_filter(days, start_date, end_date)
            
            # Limit to 1000 most recent articles for performance
            cursor.execute(f"""
                SELECT id, title, category, published_date, summary, content
                FROM articles
                WHERE category != 'Not Cybersecurity Related'
                AND threat_risk != 'NOT_RELEVANT'
                AND {date_filter}
                ORDER BY published_date DESC
                LIMIT 1000
            """)
            
            rows = cursor.fetchall()
            
            # Comprehensive threat actor database with geographic coordinates
            threat_actor_db = {
                # North Korean APTs
                'lazarus': {'name': 'Lazarus Group', 'country': 'North Korea', 'type': 'APT', 'lat': 39.0392, 'lon': 125.7625},
                'kimsuky': {'name': 'Kimsuky', 'country': 'North Korea', 'type': 'APT', 'lat': 39.0392, 'lon': 125.7625},
                'apt37': {'name': 'APT37', 'country': 'North Korea', 'type': 'APT', 'lat': 39.0392, 'lon': 125.7625},
                'apt38': {'name': 'APT38', 'country': 'North Korea', 'type': 'APT', 'lat': 39.0392, 'lon': 125.7625},
                'bluenoroff': {'name': 'BlueNoroff', 'country': 'North Korea', 'type': 'APT', 'lat': 39.0392, 'lon': 125.7625},
                'andariel': {'name': 'Andariel', 'country': 'North Korea', 'type': 'APT', 'lat': 39.0392, 'lon': 125.7625},
                
                # Russian APTs
                'apt28': {'name': 'APT28 (Fancy Bear)', 'country': 'Russia', 'type': 'APT', 'lat': 55.7558, 'lon': 37.6173},
                'apt29': {'name': 'APT29 (Cozy Bear)', 'country': 'Russia', 'type': 'APT', 'lat': 55.7558, 'lon': 37.6173},
                'sandworm': {'name': 'Sandworm', 'country': 'Russia', 'type': 'APT', 'lat': 55.7558, 'lon': 37.6173},
                'turla': {'name': 'Turla', 'country': 'Russia', 'type': 'APT', 'lat': 55.7558, 'lon': 37.6173},
                'gamaredon': {'name': 'Gamaredon', 'country': 'Russia', 'type': 'APT', 'lat': 55.7558, 'lon': 37.6173},
                'fancy bear': {'name': 'APT28 (Fancy Bear)', 'country': 'Russia', 'type': 'APT', 'lat': 55.7558, 'lon': 37.6173},
                'cozy bear': {'name': 'APT29 (Cozy Bear)', 'country': 'Russia', 'type': 'APT', 'lat': 55.7558, 'lon': 37.6173},
                
                # Chinese APTs
                'apt41': {'name': 'APT41', 'country': 'China', 'type': 'APT', 'lat': 39.9042, 'lon': 116.4074},
                'volt typhoon': {'name': 'Volt Typhoon', 'country': 'China', 'type': 'APT', 'lat': 39.9042, 'lon': 116.4074},
                'apt10': {'name': 'APT10', 'country': 'China', 'type': 'APT', 'lat': 39.9042, 'lon': 116.4074},
                'apt40': {'name': 'APT40', 'country': 'China', 'type': 'APT', 'lat': 39.9042, 'lon': 116.4074},
                'mustang panda': {'name': 'Mustang Panda', 'country': 'China', 'type': 'APT', 'lat': 39.9042, 'lon': 116.4074},
                'storm-0978': {'name': 'Storm-0978', 'country': 'China', 'type': 'APT', 'lat': 39.9042, 'lon': 116.4074},
                'aquatic panda': {'name': 'Aquatic Panda', 'country': 'China', 'type': 'APT', 'lat': 39.9042, 'lon': 116.4074},
                
                # Iranian APTs
                'apt33': {'name': 'APT33', 'country': 'Iran', 'type': 'APT', 'lat': 35.6892, 'lon': 51.3890},
                'apt34': {'name': 'APT34 (OilRig)', 'country': 'Iran', 'type': 'APT', 'lat': 35.6892, 'lon': 51.3890},
                'apt35': {'name': 'APT35', 'country': 'Iran', 'type': 'APT', 'lat': 35.6892, 'lon': 51.3890},
                'apt39': {'name': 'APT39', 'country': 'Iran', 'type': 'APT', 'lat': 35.6892, 'lon': 51.3890},
                'charming kitten': {'name': 'Charming Kitten', 'country': 'Iran', 'type': 'APT', 'lat': 35.6892, 'lon': 51.3890},
                'phosphorus': {'name': 'Phosphorus', 'country': 'Iran', 'type': 'APT', 'lat': 35.6892, 'lon': 51.3890},
                'oilrig': {'name': 'APT34 (OilRig)', 'country': 'Iran', 'type': 'APT', 'lat': 35.6892, 'lon': 51.3890},
                
                # Vietnamese APTs
                'apt32': {'name': 'APT32 (OceanLotus)', 'country': 'Vietnam', 'type': 'APT', 'lat': 21.0285, 'lon': 105.8542},
                'oceanlotus': {'name': 'APT32 (OceanLotus)', 'country': 'Vietnam', 'type': 'APT', 'lat': 21.0285, 'lon': 105.8542},
                
                # Ransomware Groups
                'lockbit': {'name': 'LockBit', 'country': 'Russia', 'type': 'Ransomware', 'lat': 55.7558, 'lon': 37.6173},
                'conti': {'name': 'Conti', 'country': 'Russia', 'type': 'Ransomware', 'lat': 55.7558, 'lon': 37.6173},
                'blackcat': {'name': 'BlackCat (ALPHV)', 'country': 'Russia', 'type': 'Ransomware', 'lat': 55.7558, 'lon': 37.6173},
                'alphv': {'name': 'BlackCat (ALPHV)', 'country': 'Russia', 'type': 'Ransomware', 'lat': 55.7558, 'lon': 37.6173},
                'cl0p': {'name': 'Cl0p', 'country': 'Russia', 'type': 'Ransomware', 'lat': 55.7558, 'lon': 37.6173},
                'clop': {'name': 'Cl0p', 'country': 'Russia', 'type': 'Ransomware', 'lat': 55.7558, 'lon': 37.6173},
                'revil': {'name': 'REvil', 'country': 'Russia', 'type': 'Ransomware', 'lat': 55.7558, 'lon': 37.6173},
                'darkside': {'name': 'DarkSide', 'country': 'Russia', 'type': 'Ransomware', 'lat': 55.7558, 'lon': 37.6173},
                'hive': {'name': 'Hive', 'country': 'Unknown', 'type': 'Ransomware', 'lat': 51.1657, 'lon': 10.4515},
                'black basta': {'name': 'Black Basta', 'country': 'Russia', 'type': 'Ransomware', 'lat': 55.7558, 'lon': 37.6173},
                'royal': {'name': 'Royal Ransomware', 'country': 'Russia', 'type': 'Ransomware', 'lat': 55.7558, 'lon': 37.6173},
                'play': {'name': 'Play Ransomware', 'country': 'Unknown', 'type': 'Ransomware', 'lat': 51.1657, 'lon': 10.4515},
                'akira': {'name': 'Akira', 'country': 'Unknown', 'type': 'Ransomware', 'lat': 51.1657, 'lon': 10.4515},
                'medusa': {'name': 'Medusa', 'country': 'Unknown', 'type': 'Ransomware', 'lat': 51.1657, 'lon': 10.4515},
                
                # Cybercrime Groups
                'fin7': {'name': 'FIN7', 'country': 'Russia', 'type': 'Cybercrime', 'lat': 55.7558, 'lon': 37.6173},
                'fin8': {'name': 'FIN8', 'country': 'Unknown', 'type': 'Cybercrime', 'lat': 51.1657, 'lon': 10.4515},
                'fin12': {'name': 'FIN12', 'country': 'Russia', 'type': 'Cybercrime', 'lat': 55.7558, 'lon': 37.6173},
                'scattered spider': {'name': 'Scattered Spider', 'country': 'USA', 'type': 'Cybercrime', 'lat': 37.0902, 'lon': -95.7129},
                'ta505': {'name': 'TA505', 'country': 'Russia', 'type': 'Cybercrime', 'lat': 55.7558, 'lon': 37.6173},
                'wizard spider': {'name': 'Wizard Spider', 'country': 'Russia', 'type': 'Cybercrime', 'lat': 55.7558, 'lon': 37.6173},
                'silence': {'name': 'Silence', 'country': 'Russia', 'type': 'Cybercrime', 'lat': 55.7558, 'lon': 37.6173},
                
                # Hacktivism
                'anonymous': {'name': 'Anonymous', 'country': 'Worldwide', 'type': 'Hacktivist', 'lat': 51.1657, 'lon': 10.4515},
                'killnet': {'name': 'KillNet', 'country': 'Russia', 'type': 'Hacktivist', 'lat': 55.7558, 'lon': 37.6173},
                'anonymous sudan': {'name': 'Anonymous Sudan', 'country': 'Sudan', 'type': 'Hacktivist', 'lat': 15.5007, 'lon': 32.5599},
            }
            
            actors_found = {}  # Use dict to prevent duplicates and aggregate data
            
            for row in rows:
                # Limit content to first 5000 characters for performance
                # Threat actors are usually mentioned early in articles
                content_text = (row['content'] or '')[:5000]
                
                text = ' '.join([
                    row['title'] or '',
                    row['summary'] or '',
                    content_text
                ]).lower()
                
                # Search for threat actor mentions
                for actor_key, actor_info in threat_actor_db.items():
                    if actor_key in text:
                        actor_name = actor_info['name']
                        
                        if actor_name not in actors_found:
                            actors_found[actor_name] = {
                                'actor': actor_name,
                                'country': actor_info['country'],
                                'type': actor_info['type'],
                                'lat': actor_info['lat'],
                                'lon': actor_info['lon'],
                                'articles': [],
                                'incident_count': 0
                            }
                        
                        # Add article reference
                        actors_found[actor_name]['articles'].append({
                            'title': row['title'],
                            'date': row['published_date'],
                            'id': row['id']
                        })
                        actors_found[actor_name]['incident_count'] += 1
            
            # SECOND PASS: Extract additional threat actor names dynamically from articles
            # Look for patterns like APT##, TA###, Storm-####, group names with "Group/Gang/Team"
            actor_patterns = [
                r'\b(APT\d+)\b',                          # APT28, APT41, etc.
                r'\b(TA\d+)\b',                            # TA505, TA558, etc.
                r'\b(Storm-\d+)\b',                        # Storm-0978, Storm-1234, etc.
                r'\b(FIN\d+)\b',                           # FIN7, FIN12, etc.
                r'\b([A-Z][a-z]+\s+(?:Group|Gang|Team))\b',  # Lazarus Group, Ember Team, etc.
                r'\b([A-Z][a-z]+(?:Spider|Bear|Panda|Kitten|Chollima))\b',  # WizardSpider, FancyBear, etc.
            ]
            
            for row in rows:
                # Limit content to first 5000 characters for performance
                content_text = (row['content'] or '')[:5000]
                
                text = ' '.join([
                    row['title'] or '',
                    row['summary'] or '',
                    content_text
                ])
                
                # Search for pattern matches
                for pattern in actor_patterns:
                    matches = re.finditer(pattern, text, re.IGNORECASE)
                    for match in matches:
                        actor_name = match.group(1)
                        
                        # Skip if already found via known database
                        if actor_name in actors_found:
                            continue
                        
                        # Determine actor type based on naming convention
                        actor_type = 'APT'
                        if 'ransomware' in text.lower():
                            actor_type = 'Ransomware'
                        elif any(x in actor_name.lower() for x in ['fin', 'ta', 'wizard', 'spider']):
                            actor_type = 'Cybercrime'
                        
                        # Default location (Unknown - Central Europe)
                        lat, lon = 51.1657, 10.4515
                        country = 'Unknown'
                        
                        # Try to infer country from context
                        if any(x in text.lower() for x in ['russia', 'russian', 'moscow']):
                            lat, lon = 55.7558, 37.6173
                            country = 'Russia'
                        elif any(x in text.lower() for x in ['china', 'chinese', 'beijing']):
                            lat, lon = 39.9042, 116.4074
                            country = 'China'
                        elif any(x in text.lower() for x in ['north korea', 'pyongyang', 'dprk']):
                            lat, lon = 39.0392, 125.7625
                            country = 'North Korea'
                        elif any(x in text.lower() for x in ['iran', 'iranian', 'tehran']):
                            lat, lon = 35.6892, 51.3890
                            country = 'Iran'
                        
                        if actor_name not in actors_found:
                            actors_found[actor_name] = {
                                'actor': actor_name,
                                'country': country,
                                'type': actor_type,
                                'lat': lat,
                                'lon': lon,
                                'articles': [],
                                'incident_count': 0
                            }
                        
                        # Add article reference
                        actors_found[actor_name]['articles'].append({
                            'title': row['title'],
                            'date': row['published_date'],
                            'id': row['id']
                        })
                        actors_found[actor_name]['incident_count'] += 1
            
            # Convert to list and format for frontend
            result = []
            for actor_name, data in actors_found.items():
                result.append({
                    'actor': data['actor'],
                    'country': data['country'],
                    'type': data['type'],
                    'lat': data['lat'],
                    'lon': data['lon'],
                    'incident_count': data['incident_count'],
                    'articles': data['articles'][:5],  # Limit to 5 most recent
                    'article_title': data['articles'][0]['title'] if data['articles'] else '',
                    'date': data['articles'][0]['date'] if data['articles'] else '',
                    'article_id': data['articles'][0]['id'] if data['articles'] else None
                })
            
            # Sort by incident count
            result.sort(key=lambda x: x['incident_count'], reverse=True)
            
            conn.close()
            return result[:limit]
            
        except Exception as e:
            print(f"❌ Error in get_threat_actor_activity: {e}")
            import traceback
            traceback.print_exc()
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
            
            cve_data = defaultdict(lambda: {'count': 0, 'articles': [], 'severity': 'UNKNOWN', 'context': [], 'score': None})
            
            for row in cursor.fetchall():
                cve = row['ioc_value']
                cve_data[cve]['count'] += 1
                cve_data[cve]['articles'].append({
                    'title': row['title'],
                    'date': row['published_date'],
                    'id': row['id']
                })
                
                # Prefer CVSS score from IOC context when present
                score = self._extract_cvss_score(row['context']) if row['context'] else None
                if score is not None:
                    # Keep the highest score seen for this CVE
                    if cve_data[cve]['score'] is None or score > cve_data[cve]['score']:
                        cve_data[cve]['score'] = score
                        cve_data[cve]['severity'] = self._cvss_to_severity(score)
                else:
                    # Fallback: infer from article threat risk (approximation)
                    if row['threat_risk'] == 'HIGH':
                        cve_data[cve]['severity'] = 'CRITICAL'
                    elif cve_data[cve]['severity'] in ['UNKNOWN', 'LOW'] and row['threat_risk'] == 'MEDIUM':
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
                    'score': data['score'],
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

