import json
import re

# Read Alaska stores
with open('/Users/dan.maguire/Downloads/WMT Stores/alaska_lucerne_stores.json', 'r') as f:
    alaska_stores = json.load(f)

print(f'Alaska stores to add: {len(alaska_stores)}')

# Read the HTML file
with open('/Users/dan.maguire/Downloads/WMT Stores/Processor_Map.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find STORES array
match = re.search(r'const STORES = (\[.*?\]);', content, re.DOTALL)
if not match:
    print('ERROR: Could not find STORES array')
    exit(1)

stores_json = match.group(1)
stores = json.loads(stores_json)

print(f'Current stores: {len(stores)}')

# Check for existing Alaska stores
existing_alaska = [s for s in stores if s.get('state') == 'AK']
print(f'Existing Alaska stores: {len(existing_alaska)}')

# Add new Alaska stores (avoiding duplicates by store number)
existing_sns = {s['sn'] for s in stores}
added = 0

for ak_store in alaska_stores:
    if ak_store['sn'] not in existing_sns:
        stores.append(ak_store)
        added += 1
    else:
        print(f"Skipping duplicate store #{ak_store['sn']}")

print(f'Added {added} new Alaska stores')
print(f'Total stores after: {len(stores)}')

# Convert back to compact JSON
new_stores_json = json.dumps(stores, separators=(',', ':'))

# Replace in content
new_content = content.replace(match.group(0), f'const STORES = {new_stores_json};')

# Write back
with open('/Users/dan.maguire/Downloads/WMT Stores/Processor_Map.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('✓ Alaska Lucerne stores added to map')

# Show summary by retailer
from collections import Counter
alaska_retailers = Counter(s['retailer'] for s in stores if s['state'] == 'AK')
print('\nAlaska stores by retailer:')
for retailer, count in alaska_retailers.most_common():
    print(f'  {retailer}: {count}')
