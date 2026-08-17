import json
import re

# Read the HTML file
with open('/Users/dan.maguire/Downloads/WMT Stores/Processor_Map.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract STORES array
match = re.search(r'const STORES = (\[.*?\]);', content, re.DOTALL)
if match:
    stores_json = match.group(1)
    stores = json.loads(stores_json)
    
    print(f'Total stores: {len(stores)}')
    
    # First, let's see what the actual store names look like for Crystal Creamery and Hollandia stores
    crystal_stores = [s for s in stores if s['processor'] == 'Crystal Creamery']
    hollandia_stores = [s for s in stores if s['processor'] == 'Hollandia']
    
    print(f'\nCrystal Creamery stores: {len(crystal_stores)}')
    print('Sample store names:')
    for store in crystal_stores[:5]:
        print(f'  Store #{store["sn"]}: {store.get("name", "N/A")} - {store["city"]}, {store["state"]}')
    
    print(f'\nHollandia stores: {len(hollandia_stores)}')
    print('Sample store names:')
    for store in hollandia_stores[:5]:
        print(f'  Store #{store["sn"]}: {store.get("name", "N/A")} - {store["city"]}, {store["state"]}')
    
    # Check if stores have a 'name' field that might indicate the banner
    print('\nChecking for store name patterns...')
    
    # Count by what appears in the name field
    name_patterns = {}
    for store in crystal_stores + hollandia_stores:
        name = store.get('name', '').lower()
        if 'vons' in name or "von's" in name:
            banner = 'Vons'
        elif 'safeway' in name:
            banner = 'Safeway'
        elif 'albertsons' in name or 'albertson' in name:
            banner = 'Albertsons'
        else:
            banner = 'Unknown'
        
        if banner not in name_patterns:
            name_patterns[banner] = 0
        name_patterns[banner] += 1
    
    print('\nBanner distribution in Crystal Creamery + Hollandia stores:')
    for banner, count in sorted(name_patterns.items()):
        print(f'  {banner}: {count} stores')
    
else:
    print('ERROR: Could not find STORES array in HTML file')
