import json
import re
import time
from urllib.parse import quote
from urllib.request import urlopen

# Read misplaced stores
with open('/tmp/misplaced.json', 'r') as f:
    misplaced = json.load(f)

print(f"Geocoding {len(misplaced)} stores...\n")

# Geocode each store using Nominatim (free, no API key needed)
fixes = {}
for i, store in enumerate(misplaced, 1):
    sn = store['sn']
    addr = store['addr']
    city = store['city']
    state = 'CA'  # We know they should be CA
    zip_code = store['zip']
    
    # Build query
    query = f"{addr}, {city}, {state} {zip_code}"
    encoded = quote(query)
    url = f"https://nominatim.openstreetmap.org/search?q={encoded}&format=json&limit=1"
    
    print(f"{i}/{len(misplaced)} - #{sn}: {city}, CA")
    print(f"  Query: {query}")
    
    try:
        # Be nice to the API - wait between requests
        time.sleep(1)
        
        response = urlopen(url)
        data = json.loads(response.read())
        
        if data:
            lat = float(data[0]['lat'])
            lon = float(data[0]['lon'])
            
            # Verify it's actually in California
            if 32.5 <= lat <= 42.0 and -124.5 <= lon <= -114.0:
                fixes[sn] = {'lat': lat, 'lon': lon}
                print(f"  ✓ Found: ({lat:.6f}, {lon:.6f})")
            else:
                print(f"  ✗ Result outside CA: ({lat:.6f}, {lon:.6f})")
        else:
            print(f"  ✗ No results found")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    print()

print(f"\nSuccessfully geocoded: {len(fixes)}/{len(misplaced)}")

# Save fixes
with open('/tmp/geocode_fixes.json', 'w') as f:
    json.dump(fixes, f, indent=2)

print("Saved to /tmp/geocode_fixes.json")
