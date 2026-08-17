import json
import re

# Define the new region mapping
STATE_TO_REGION = {
    # Northeast
    'CT': 'Northeast', 'ME': 'Northeast', 'MA': 'Northeast', 
    'NH': 'Northeast', 'RI': 'Northeast', 'VT': 'Northeast',
    
    # Mid-Atlantic
    'DE': 'Mid-Atlantic', 'MD': 'Mid-Atlantic', 'NJ': 'Mid-Atlantic',
    'NY': 'Mid-Atlantic', 'PA': 'Mid-Atlantic', 'DC': 'Mid-Atlantic',
    
    # Southeast
    'AL': 'Southeast', 'FL': 'Southeast', 'GA': 'Southeast',
    'KY': 'Southeast', 'MS': 'Southeast', 'NC': 'Southeast',
    'SC': 'Southeast', 'TN': 'Southeast', 'VA': 'Southeast',
    'WV': 'Southeast',
    
    # Midwest
    'IL': 'Midwest', 'IN': 'Midwest', 'IA': 'Midwest',
    'MI': 'Midwest', 'MN': 'Midwest', 'MO': 'Midwest',
    'ND': 'Midwest', 'OH': 'Midwest', 'SD': 'Midwest',
    'WI': 'Midwest',
    
    # Southwest
    'AR': 'Southwest', 'KS': 'Southwest', 'LA': 'Southwest',
    'NE': 'Southwest', 'NM': 'Southwest', 'OK': 'Southwest',
    'TX': 'Southwest',
    
    # West
    'AZ': 'West', 'CA': 'West', 'CO': 'West',
    'NV': 'West', 'UT': 'West',
    
    # Pacific Northwest
    'AK': 'Pacific Northwest', 'ID': 'Pacific Northwest', 'MT': 'Pacific Northwest',
    'OR': 'Pacific Northwest', 'WA': 'Pacific Northwest', 'WY': 'Pacific Northwest'
}

# Read the HTML file
with open('/Users/dan.maguire/Downloads/WMT Stores/WMT Store Map.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract STORES array
match = re.search(r'const STORES = (\[.*?\]);', content, re.DOTALL)
if match:
    stores_json = match.group(1)
    stores = json.loads(stores_json)
    
    print(f'Total stores: {len(stores)}')
    
    # Update regions for all stores
    updated_count = 0
    region_counts = {}
    
    for store in stores:
        state = store['state']
        old_region = store.get('region', 'Unknown')
        new_region = STATE_TO_REGION.get(state, 'Unknown')
        
        if new_region != 'Unknown':
            store['region'] = new_region
            updated_count += 1
            
            if new_region not in region_counts:
                region_counts[new_region] = 0
            region_counts[new_region] += 1
    
    print(f'\nUpdated {updated_count} stores')
    print(f'\nNew region distribution:')
    for region in sorted(region_counts.keys()):
        print(f'  {region}: {region_counts[region]} stores')
    
    # Convert back to JSON
    new_stores_json = json.dumps(stores, separators=(',', ':'))
    
    # Replace in content
    new_content = content.replace(match.group(0), f'const STORES = {new_stores_json};')
    
    # Write back
    with open('/Users/dan.maguire/Downloads/WMT Stores/WMT Store Map.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print('\n✓ Regions remapped successfully')
else:
    print('ERROR: Could not find STORES array in HTML file')
