import json
import re

# Read the HTML file
with open('/Users/dan.maguire/Downloads/WMT Stores/WMT Store Map.html', 'r') as f:
    html_content = f.read()

# Extract the STORES array using regex
match = re.search(r'const STORES = (\[.*?\]);', html_content, re.DOTALL)
if not match:
    print("ERROR: Could not find STORES array")
    exit(1)

stores_json = match.group(1)
stores = json.loads(stores_json)

print(f"Total stores loaded: {len(stores)}")

# Step 1: Find and remove closed stores
closed_addresses = ['Fletcher Pkwy', 'Imperial Ave', 'W. Florida Ave', 'W Florida Ave']
stores_to_remove = []

for i, store in enumerate(stores):
    addr = store.get('addr', '')
    city = store.get('city', '')
    
    # Check for closed stores
    if any(closed_addr in addr for closed_addr in closed_addresses):
        if ('Fletcher Pkwy' in addr and 'El Cajon' in city) or \
           ('Imperial Ave' in addr and 'San Diego' in city) or \
           ('Florida Ave' in addr and 'Hemet' in city):
            stores_to_remove.append(i)
            print(f"CLOSED - Remove #{store['sn']}: {addr}, {city}, {store['state']}")

# Remove closed stores (in reverse order to maintain indices)
for idx in reversed(stores_to_remove):
    del stores[idx]

print(f"\nRemoved {len(stores_to_remove)} closed stores")
print(f"Remaining stores: {len(stores)}")

# Step 2: Find geocoding mismatches
# California boundaries: lat 32.5-42, lon -124.5 to -114
mismatches = []

for i, store in enumerate(stores):
    lat = store['lat']
    lon = store['lon']
    state = store['state']
    
    # Check if coordinates are in California but state is not CA
    in_ca_coords = (32.5 <= lat <= 42.0 and -124.5 <= lon <= -114.0)
    
    if in_ca_coords and state != 'CA':
        mismatches.append({
            'index': i,
            'store': store,
            'issue': 'coords_in_CA_but_wrong_state'
        })
        print(f"MISMATCH - #{store['sn']}: {store['city']}, {state} at ({lat:.4f}, {lon:.4f}) - coords in CA")

print(f"\nTotal geocoding mismatches found: {len(mismatches)}")

# Step 3: Fix the mismatches by setting state to CA
for mismatch in mismatches:
    idx = mismatch['index']
    stores[idx]['state'] = 'CA'
    print(f"FIXED - #{stores[idx]['sn']}: {stores[idx]['city']} changed from {mismatch['store']['state']} to CA")

# Step 4: Write the fixed data back
fixed_stores_json = json.dumps(stores, separators=(',', ': '))
new_html = html_content.replace(stores_json, fixed_stores_json)

# Save the fixed HTML
with open('/Users/dan.maguire/Downloads/WMT Stores/WMT Store Map.html', 'w') as f:
    f.write(new_html)

print(f"\n✓ Fixed HTML file saved")
print(f"✓ Removed {len(stores_to_remove)} closed stores")
print(f"✓ Fixed {len(mismatches)} geocoding mismatches")
print(f"✓ Total stores now: {len(stores)}")
