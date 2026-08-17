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
    
    # Filter out Alaska stores
    filtered_stores = [s for s in stores if s['state'] != 'AK']
    
    print(f'Original stores: {len(stores)}')
    print(f'Alaska stores removed: {len(stores) - len(filtered_stores)}')
    print(f'Remaining stores: {len(filtered_stores)}')
    
    # Convert back to JSON
    new_stores_json = json.dumps(filtered_stores, separators=(',', ':'))
    
    # Replace in content
    new_content = content.replace(match.group(0), f'const STORES = {new_stores_json};')
    
    # Write back
    with open('/Users/dan.maguire/Downloads/WMT Stores/WMT Store Map.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print('✓ Alaska stores removed from map')
