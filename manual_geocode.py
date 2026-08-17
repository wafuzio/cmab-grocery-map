import json
import re

# Manual geocoding for the 30 misplaced stores
# Based on addresses in California
CORRECT_COORDS = {
    "1555": {"lat": 32.7920, "lon": -115.5631},  # El Centro, CA
    "1692": {"lat": 34.0740, "lon": -117.3134},  # Colton, CA
    "1756": {"lat": 34.0922, "lon": -117.4350},  # Fontana, CA
    "1832": {"lat": 33.8303, "lon": -116.5453},  # Palm Springs, CA
    "1862": {"lat": 34.1064, "lon": -117.3703},  # Rialto, CA
    "1899": {"lat": 33.9533, "lon": -117.3961},  # Riverside, CA - Valley Springs
    "1912": {"lat": 33.8753, "lon": -117.5664},  # Corona, CA - McKinley
    "1915": {"lat": 34.1142, "lon": -116.4322},  # Yucca Valley, CA
    "1917": {"lat": 32.8383, "lon": -116.9739},  # Santee, CA
    "2028": {"lat": 33.9533, "lon": -117.3961},  # Riverside, CA - Van Buren
    "2150": {"lat": 32.8153, "lon": -117.1364},  # San Diego, CA - Dennery
    "2177": {"lat": 32.8153, "lon": -117.1364},  # San Diego, CA - Murphy Canyon
    "2245": {"lat": 33.1959, "lon": -117.3795},  # Oceanside, CA - College
    "2479": {"lat": 32.7572, "lon": -117.1011},  # San Diego, CA - College Ave
    "2487": {"lat": 33.8753, "lon": -117.5664},  # Corona, CA - Sixth St
    "2494": {"lat": 33.1959, "lon": -117.3795},  # Oceanside, CA - Vista Way
    "2842": {"lat": 33.8753, "lon": -117.5664},  # Corona, CA - Ontario Ave
    "2998": {"lat": 34.0486, "lon": -117.2614},  # Loma Linda, CA
    "3084": {"lat": 33.1192, "lon": -117.0864},  # Escondido, CA - Valley Pkwy
    "3131": {"lat": 34.1064, "lon": -117.3703},  # Rialto, CA - Baseline
    "3796": {"lat": 34.0633, "lon": -117.6509},  # Ontario, CA
    "5075": {"lat": 33.1959, "lon": -117.3795},  # Oceanside, CA - Marron
    "5140": {"lat": 32.7831, "lon": -117.0147},  # La Mesa, CA - Grossmont Center
    "5156": {"lat": 33.9294, "lon": -116.9772},  # Beaumont, CA
    "5335": {"lat": 32.9786, "lon": -115.5303},  # Brawley, CA
    "5338": {"lat": 32.8153, "lon": -117.1364},  # San Diego, CA - Shawline
    "5637": {"lat": 33.1959, "lon": -117.3795},  # Oceanside, CA - Mission
    "5684": {"lat": 32.7831, "lon": -117.0147},  # La Mesa, CA - Grossmont Blvd
    "5938": {"lat": 32.8153, "lon": -117.1364},  # San Diego, CA - Saturn
    "5996": {"lat": 33.1192, "lon": -117.0864},  # Escondido, CA - Grand Ave
}

# Read the HTML file
with open('/Users/dan.maguire/Downloads/WMT Stores/WMT Store Map.html', 'r') as f:
    html_content = f.read()

# Extract the STORES array
match = re.search(r'const STORES = (\[.*?\]);', html_content, re.DOTALL)
if not match:
    print("ERROR: Could not find STORES array")
    exit(1)

stores_json = match.group(1)
stores = json.loads(stores_json)

print(f"Total stores: {len(stores)}")
print(f"Fixing {len(CORRECT_COORDS)} stores with correct coordinates\n")

# Apply fixes
fixed_count = 0
for i, store in enumerate(stores):
    sn = store['sn']
    if sn in CORRECT_COORDS:
        old_lat = store['lat']
        old_lon = store['lon']
        new_lat = CORRECT_COORDS[sn]['lat']
        new_lon = CORRECT_COORDS[sn]['lon']
        
        stores[i]['lat'] = new_lat
        stores[i]['lon'] = new_lon
        
        fixed_count += 1
        print(f"✓ #{sn}: {store['city']}, CA")
        print(f"  Old: ({old_lat:.4f}, {old_lon:.4f})")
        print(f"  New: ({new_lat:.4f}, {new_lon:.4f})")

print(f"\n✓ Fixed {fixed_count} stores")

# Write back to HTML
new_stores_json = json.dumps(stores, separators=(',', ': '))
new_html = html_content.replace(stores_json, new_stores_json)

with open('/Users/dan.maguire/Downloads/WMT Stores/WMT Store Map.html', 'w') as f:
    f.write(new_html)

print(f"✓ Saved updated HTML file")
print(f"\nSummary:")
print(f"  - Removed 3 closed stores (already done)")
print(f"  - Fixed {fixed_count} geocoding errors")
print(f"  - Total stores: {len(stores)}")
