import json
import re

# Read the HTML file
with open('/Users/dan.maguire/Downloads/WMT Stores/WMT Store Map.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract STORES array
match = re.search(r'const STORES = (\[.*?\]);', content, re.DOTALL)
if match:
    stores_json = match.group(1)
    stores = json.loads(stores_json)
    
    # Check for Alaska stores
    alaska_stores = [s for s in stores if s['state'] == 'AK']
    
    print(f'Total stores: {len(stores)}')
    print(f'Alaska stores: {len(alaska_stores)}')
    
    if alaska_stores:
        print('\nAlaska stores found:')
        for store in alaska_stores:
            print(f'  {store["retailer"]} #{store["sn"]} - {store["city"]}, {store["state"]} ({store["processor"]})')
    else:
        print('\nNo Alaska stores found in the data.')
