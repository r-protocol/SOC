# db_utils.py
import sqlite3
import os
from config import DATABASE_PATH
from logging_utils import log_success, log_error

def initialize_database():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Create articles table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            url TEXT UNIQUE NOT NULL,
            published_date TEXT NOT NULL,
            content TEXT,
            summary TEXT,
            threat_risk TEXT,
            category TEXT,
            recommendations TEXT
        )
    """)
    
    # Create IOCs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS iocs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            article_id INTEGER,
            ioc_type TEXT NOT NULL,
            ioc_value TEXT NOT NULL,
            context TEXT,
            FOREIGN KEY (article_id) REFERENCES articles (id),
            UNIQUE(article_id, ioc_type, ioc_value)
        )
    """)
    
    # Create KQL queries table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS kql_queries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            article_id INTEGER,
            query_name TEXT NOT NULL,
            query_type TEXT NOT NULL,
            platform TEXT,
            ioc_type TEXT,
            ioc_count INTEGER,
            kql_query TEXT NOT NULL,
            tables_used TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (article_id) REFERENCES articles (id)
        )
    """)
    
    conn.commit()
    conn.close()
    log_success("Database initialized successfully.")

def get_existing_urls():
    if not os.path.exists(DATABASE_PATH):
        return set()
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT url FROM articles")
    urls = {row[0] for row in cursor.fetchall()}
    conn.close()
    return urls

def store_analyzed_data(analyzed_data_list):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    stored_count = 0
    article_ids = []
    
    for data in analyzed_data_list:
        try:
            summary_text = data.get('summary', 'N/A')
            import json
            recommendations_json = json.dumps(data.get('recommendations', []))
            cursor.execute("""
                INSERT OR IGNORE INTO articles
                (title, url, published_date, content, summary, threat_risk, category, recommendations)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data['title'], data['url'], data['published_date'], data.get('content'),
                summary_text, data.get('threat_risk'), data.get('category'),
                recommendations_json
            ))
            if cursor.rowcount > 0:
                stored_count += 1
                article_ids.append((cursor.lastrowid, data))
        except sqlite3.Error as e:
            log_error(f"DB error for {data['title']}: {e}")
    
    conn.commit()
    conn.close()
    log_success(f"Stored {stored_count} new articles in the database.")
    return article_ids


def store_iocs(article_id, iocs_dict):
    """Store extracted IOCs for an article"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    stored_count = 0
    
    for ioc_type, ioc_list in iocs_dict.items():
        for ioc in ioc_list:
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO iocs
                    (article_id, ioc_type, ioc_value, context)
                    VALUES (?, ?, ?, ?)
                """, (
                    article_id,
                    ioc_type,
                    ioc['value'],
                    ioc.get('context', '')
                ))
                if cursor.rowcount > 0:
                    stored_count += 1
            except sqlite3.Error as e:
                log_error(f"Error storing IOC {ioc['value']}: {e}")
    
    conn.commit()
    conn.close()
    return stored_count


def store_kql_queries(article_id, queries):
    """Store generated KQL queries for an article"""
    import json
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    stored_count = 0
    
    for query in queries:
        try:
            cursor.execute("""
                INSERT INTO kql_queries
                (article_id, query_name, query_type, platform, ioc_type, ioc_count, kql_query, tables_used)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                article_id,
                query['name'],
                query['type'],
                query['platform'],
                query.get('ioc_type', ''),
                query.get('ioc_count', 0),
                query['query'],
                json.dumps(query.get('tables', []))
            ))
            stored_count += 1
        except sqlite3.Error as e:
            log_error(f"Error storing KQL query: {e}")
    
    conn.commit()
    conn.close()
    return stored_count
