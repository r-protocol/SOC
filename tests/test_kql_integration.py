import sqlite3
from kql_generator import IOCExtractor, KQLQueryGenerator
from db_utils import store_iocs, store_kql_queries

# Connect to database
conn = sqlite3.connect('threat_intel.db')
cursor = conn.cursor()

# Check tables
print("Database Tables:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
for row in cursor.fetchall():
    print(f"  - {row[0]}")

# Get a sample article
cursor.execute("SELECT id, title, content, threat_risk FROM articles WHERE content IS NOT NULL LIMIT 1")
result = cursor.fetchone()

if result:
    article_id, title, content, risk = result
    print(f"\n\nTesting KQL Generation on: {title}")
    print(f"Risk Level: {risk}")
    
    # Create test article dict
    test_article = {
        'title': title,
        'content': content,
        'threat_risk': risk
    }
    
    # Extract IOCs
    extractor = IOCExtractor()
    iocs = extractor.extract_all(content)
    
    print(f"\nExtracted IOCs:")
    for ioc_type, ioc_list in iocs.items():
        if ioc_list:
            print(f"  {ioc_type}: {len(ioc_list)}")
            for ioc in ioc_list[:2]:  # Show first 2
                print(f"    - {ioc['value']}")
    
    # Generate KQL queries
    generator = KQLQueryGenerator()
    queries = generator.generate_queries(test_article)
    
    print(f"\nGenerated {len(queries)} KQL Queries:")
    for i, query in enumerate(queries[:3], 1):  # Show first 3
        print(f"\n  Query {i}: {query['name'][:60]}...")
        print(f"    Type: {query['type']}, Platform: {query['platform']}")
        print(f"    IOC Type: {query.get('ioc_type', 'N/A')} (Count: {query.get('ioc_count', 0)})")
    
    # Store them
    if iocs:
        ioc_count = store_iocs(article_id, iocs)
        print(f"\n✅ Stored {ioc_count} IOCs to database")
    
    if queries:
        query_count = store_kql_queries(article_id, queries)
        print(f"✅ Stored {query_count} KQL queries to database")
    
    # Verify storage
    cursor.execute("SELECT COUNT(*) FROM iocs WHERE article_id = ?", (article_id,))
    print(f"\n📊 Total IOCs in DB for this article: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM kql_queries WHERE article_id = ?", (article_id,))
    print(f"📊 Total KQL queries in DB for this article: {cursor.fetchone()[0]}")
else:
    print("No articles with content found in database")

conn.close()
print("\n✅ Test complete!")
