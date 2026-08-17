import json
import re
import time
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

# Initialize geocoder
geolocator = Nominatim(user_agent="milkpep_store_mapper")

# Read the HTML file
with open('/Users/dan.maguire/Downloads/WMT Stores/Processor_Map.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find STORES array
match = re.search(r'const STORES = (\[.*?\]);', content, re.DOTALL)
if not match:
    print('ERROR: Could not find STORES array')
    exit(1)

stores = json.loads(match.group(1))

# Find Alaska stores with invalid coordinates
alaska_stores = [s for s in stores if s.get('state') == 'AK' and (s.get('lat', 0) == 0 or s.get('lon', 0) == 0)]

print(f'Found {len(alaska_stores)} Alaska stores needing geocoding')

# Geocode each store
geocoded = 0
failed = []

for store in alaska_stores:
    address = f"{store['addr']}, {store['city']}, AK {store['zip']}"
    print(f"\nGeocoding: {store['retailer']} #{store['sn']}")
    print(f"  Address: {address}")
    
    try:
        location = geolocator.geocode(address, timeout=10)
        
        if location:
            # Update the store in the main stores array
            for s in stores:
                if s['sn'] == store['sn'] and s['state'] == 'AK':
                    s['lat'] = location.latitude
                    s['lon'] = location.longitude
                    print(f"  ✓ Found: {location.latitude}, {location.longitude}")
                    geocoded += 1
                    break
        else:
            print(f"  ✗ Not found")
            failed.append(store)
        
        # Be nice to the geocoding service
        time.sleep(1)
        
    except (GeocoderTimedOut, GeocoderServiceError) as e:
        print(f"  ✗ Error: {e}")
        failed.append(store)
        time.sleep(2)

print(f'\n\nGeocoding complete:')
print(f'  Successfully geocoded: {geocoded}')
print(f'  Failed: {len(failed)}')

if failed:
    print('\nFailed stores:')
    for store in failed:
        print(f"  {store['retailer']} #{store['sn']} - {store['city']}, AK")

# Update the HTML file
new_stores_json = json.dumps(stores, separators=(',', ':'))
new_content = content.replace(match.group(0), f'const STORES = {new_stores_json};')

with open('/Users/dan.maguire/Downloads/WMT Stores/Processor_Map.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('\n✓ Updated Processor_Map.html with geocoded coordinates')
