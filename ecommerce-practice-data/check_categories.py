import json
from collections import Counter

with open('massive_catalog.json', 'r') as f:
    data = json.load(f)

categories = [item['category'] for item in data]
print("\n--- Available Categories ---")
for cat, count in Counter(categories).most_common():
    print(f"{cat}: {count} products")
