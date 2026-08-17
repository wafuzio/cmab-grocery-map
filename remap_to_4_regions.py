import json
import re

# Define the 4 Census Bureau regions (excluding Hawaii)
STATE_TO_REGION = {
    # West
    'AK': 'West', 'AZ': 'West', 'CA': 'West', 'CO': 'West',
    'ID': 'West', 'MT': 'West', 'NV': 'West', 'NM': 'West',
    'OR': 'West', 'UT': 'West', 'WA': 'West', 'WY': 'West',
    
    # Midwest
    'IL': 'Midwest', 'IN': 'Midwest', 'IA': 'Midwest', 'KS': 'Midwest',
    'MI': 'Midwest', 'MN': 'Midwest', 'MO': 'Midwest', 'NE': 'Midwest',
    'ND': 'Midwest', 'OH': 'Midwest', 'SD': 'Midwest', 'WI': 'Midwest',
    
    # Northeast
    'CT': 'Northeast', 'ME': 'Northeast', 'MA': 'Northeast', 'NH': 'Northeast',
    'NJ': 'Northeast', 'NY': 'Northeast', 'PA': 'Northeast', 'RI': 'Northeast',
    'VT': 'Northeast', 'DE': 'Northeast', 'MD': 'Northeast', 'DC': 'Northeast',
    
    # South
    'AL': 'South', 'AR': 'South', 'FL': 'South', 'GA': 'South',
    'KY': 'South', 'LA': 'South', 'MS': 'South', 'NC': 'South',
    'OK': 'South', 'SC': 'South', 'TN': 'South', 'TX': 'South',
    'VA': 'South', 'WV': 'South'
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
    excluded_count = 0
    
    for store in stores:
        state = store['state']
        
        # Skip Hawaii
        if state == 'HI':
            excluded_count += 1
            continue
            
        new_region = STATE_TO_REGION.get(state, 'Unknown')
        
        if new_region != 'Unknown':
            store['region'] = new_region
            updated_count += 1
            
            if new_region not in region_counts:
                region_counts[new_region] = 0
            region_counts[new_region] += 1
    
    print(f'\nUpdated {updated_count} stores')
    if excluded_count > 0:
        print(f'Excluded {excluded_count} Hawaii stores')
    
    print(f'\nNew 4-region distribution:')
    for region in ['West', 'Midwest', 'Northeast', 'South']:
        count = region_counts.get(region, 0)
        print(f'  {region}: {count} stores')
    
    # Convert back to JSON
    new_stores_json = json.dumps(stores, separators=(',', ':'))
    
    # Replace in content
    new_content = content.replace(match.group(0), f'const STORES = {new_stores_json};')
    
    # Write back
    with open('/Users/dan.maguire/Downloads/WMT Stores/WMT Store Map.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print('\n✓ Regions remapped to 4 Census Bureau regions successfully')
else:
    print('ERROR: Could not find STORES array in HTML file')
