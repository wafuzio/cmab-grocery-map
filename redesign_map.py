import json
import re

# Read the current HTML
with open('/Users/dan.maguire/Downloads/WMT Stores/WMT Store Map.html', 'r') as f:
    content = f.read()

# Extract stores
match = re.search(r'const STORES = (\[.*?\]);', content, re.DOTALL)
stores = json.loads(match.group(1))

# Define US regions
STATE_REGIONS = {
    'Northeast': ['ME', 'NH', 'VT', 'MA', 'RI', 'CT', 'NY', 'NJ', 'PA'],
    'Southeast': ['DE', 'MD', 'DC', 'VA', 'WV', 'NC', 'SC', 'GA', 'FL', 'KY', 'TN', 'AL', 'MS', 'AR', 'LA'],
    'Midwest': ['OH', 'MI', 'IN', 'IL', 'WI', 'MN', 'IA', 'MO', 'ND', 'SD', 'NE', 'KS'],
    'Southwest': ['TX', 'OK', 'NM', 'AZ'],
    'West': ['CO', 'WY', 'MT', 'ID', 'UT', 'NV', 'CA', 'OR', 'WA', 'AK', 'HI']
}

# Add region to each store
for store in stores:
    state = store['state']
    for region, states in STATE_REGIONS.items():
        if state in states:
            store['region'] = region
            break
    else:
        store['region'] = 'Other'

print(f"Added regions to {len(stores)} stores")

# Count by region
region_counts = {}
for store in stores:
    region = store['region']
    region_counts[region] = region_counts.get(region, 0) + 1

print("\nStores by region:")
for region, count in sorted(region_counts.items()):
    print(f"  {region}: {count}")

# Write back
new_stores_json = json.dumps(stores, separators=(',', ': '))
new_content = content.replace(match.group(1), new_stores_json)

with open('/Users/dan.maguire/Downloads/WMT Stores/WMT Store Map.html', 'w') as f:
    f.write(new_content)

print("\n✓ Updated stores with region data")
