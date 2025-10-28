import json
from datetime import datetime, timedelta

with open('dashboard/frontend/public/data.json', encoding='utf-8') as f:
    data = json.load(f)

articles = data['articles']
print(f'Total articles: {len(articles)}')

dates = sorted([a['published_date'] for a in articles])
print(f'Date range: {dates[0]} to {dates[-1]}')

# Count by date ranges
today = datetime.now()
seven_days_ago = (today - timedelta(days=7)).strftime('%Y-%m-%d')
thirty_days_ago = (today - timedelta(days=30)).strftime('%Y-%m-%d')

count_7 = sum(1 for d in dates if d >= seven_days_ago)
count_30 = sum(1 for d in dates if d >= thirty_days_ago)
count_all = len(articles)

print(f'\nArticles from last 7 days: {count_7}')
print(f'Articles from last 30 days: {count_30}')
print(f'All articles: {count_all}')
