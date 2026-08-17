import json
import re

# Read the HTML file
with open('/Users/dan.maguire/Downloads/WMT Stores/Processor_Map.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find STORES array
match = re.search(r'const STORES = (\[.*?\]);', content, re.DOTALL)
if match:
    stores = json.loads(match.group(1))
    
    # Store numbers to remove
    closed_stores = ['3524', '5638', '5008']
    
    print(f'Total stores before: {len(stores)}')
    
    # Find and display the stores to be removed
    print('\nStores to remove:')
    for sn in closed_stores:
        for store in stores:
            if store.get('sn') == sn and store.get('retailer') == 'Walmart':
                print(f"  Walmart #{store['sn']} - {store['city']}, {store['state']} - {store['addr']}")
    
    # Remove the closed stores
    stores_filtered = [s for s in stores if not (s.get('retailer') == 'Walmart' and s.get('sn') in closed_stores)]
    
    removed = len(stores) - len(stores_filtered)
    print(f'\nRemoved: {removed} stores')
    print(f'Total stores after: {len(stores_filtered)}')
    
    # Update the HTML file
    new_stores_json = json.dumps(stores_filtered, separators=(',', ':'))
    new_content = content.replace(match.group(0), f'const STORES = {new_stores_json};')
    
    with open('/Users/dan.maguire/Downloads/WMT Stores/Processor_Map.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print('\n✓ Updated Processor_Map.html')
else:
    print('ERROR: Could not find STORES array')
