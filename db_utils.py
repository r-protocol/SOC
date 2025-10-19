# db_utils.py
import sqlite3
import os
from config import DATABASE_PATH
from logging_utils import log_success, log_error

def initialize_database():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
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
        except sqlite3.Error as e:
            log_error(f"DB error for {data['title']}: {e}")
    conn.commit()
    conn.close()
    log_success(f"Stored {stored_count} new articles in the database.")
