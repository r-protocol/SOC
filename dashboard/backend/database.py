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
    
    def get_pipeline_overview(self):
        """Get pipeline statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Get total articles
            cursor.execute("SELECT COUNT(*) as total FROM articles")
            total_articles = cursor.fetchone()['total']
            
            # Get articles from last 7 days
            seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()
            cursor.execute("""
                SELECT COUNT(*) as recent 
                FROM articles 
                WHERE published_date >= ?
            """, (seven_days_ago,))
            recent_articles = cursor.fetchone()['recent']
            
            # Get HIGH risk count
            cursor.execute("""
                SELECT COUNT(*) as critical 
                FROM articles 
                WHERE threat_risk = 'HIGH'
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
    
    def get_category_distribution(self):
        """Get threat distribution by category"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT category, COUNT(*) as count
                FROM articles
                WHERE category IS NOT NULL
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
    
    def get_threat_timeline(self, days=7):
        """Get threat counts over time"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            start_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            cursor.execute("""
                SELECT 
                    DATE(published_date) as date,
                    threat_risk,
                    COUNT(*) as count
                FROM articles
                WHERE published_date >= ?
                GROUP BY DATE(published_date), threat_risk
                ORDER BY date
            """, (start_date,))
            
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
    
    def get_recent_threats(self, limit=10, risk_filter=None):
        """Get recent high-priority threats"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            query = """
                SELECT 
                    id, title, summary, category, threat_risk, 
                    published_date, url
                FROM articles
            """
            
            params = []
            if risk_filter:
                query += " WHERE threat_risk = ?"
                params.append(risk_filter)
            
            query += " ORDER BY published_date DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            
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
                
                threats.append({
                    "id": row['id'],
                    "title": row['title'],
                    "summary": row['summary'][:200] if row['summary'] else '',
                    "category": row['category'] or 'Uncategorized',
                    "risk_level": row['threat_risk'] or 'LOW',
                    "published_date": row['published_date'],
                    "source_url": row['url'],
                    "ioc_count": ioc_count
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
        """Get RSS feed statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT url, COUNT(*) as count
                FROM articles
                GROUP BY url
            """)
            
            feed_stats = []
            feed_names = {
                "bleepingcomputer": "BleepingComputer",
                "thehackernews": "The Hacker News",
                "darkreading": "Dark Reading",
                "threatpost": "Threatpost",
                "krebsonsecurity": "Krebs on Security"
            }
            
            source_counts = defaultdict(int)
            for row in cursor.fetchall():
                source = row['url'] or ""
                for key in feed_names.keys():
                    if key in source.lower():
                        source_counts[key] += row['count']
                        break
            
            for key, name in feed_names.items():
                count = source_counts.get(key, 0)
                feed_stats.append({
                    "name": name,
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
            cursor.execute("""
                SELECT * FROM articles WHERE id = ?
            """, (article_id,))
            
            row = cursor.fetchone()
            
            if not row:
                conn.close()
                return None
            
            # Get IOCs for this article
            iocs = []
            try:
                cursor.execute("""
                    SELECT ioc_type, ioc_value, context 
                    FROM iocs 
                    WHERE article_id = ?
                """, (article_id,))
                iocs = [dict(row) for row in cursor.fetchall()]
            except:
                pass
            
            # Get KQL queries for this article
            kql_queries = []
            try:
                cursor.execute("""
                    SELECT query_name, query_text, query_type
                    FROM kql_queries
                    WHERE article_id = ?
                """, (article_id,))
                kql_queries = [dict(row) for row in cursor.fetchall()]
            except:
                pass
            
            conn.close()
            
            return {
                "id": row['id'],
                "title": row['title'],
                "summary": row['summary'],
                "content": row.get('content', ''),
                "category": row['category'],
                "risk_level": row['threat_risk'],
                "published_date": row['published_date'],
                "source_url": row['url'],
                "recommendations": row.get('recommendations', ''),
                "iocs": iocs,
                "kql_queries": kql_queries
            }
        except Exception as e:
            print(f"❌ Error in get_article_details: {e}")
            conn.close()
            return None
    
    def get_threat_families(self):
        """Extract threat family names for word cloud"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT category, title FROM articles")
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
