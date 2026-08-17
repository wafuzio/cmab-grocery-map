import json
import time
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

# Initialize geocoder
geolocator = Nominatim(user_agent="gopuff_mfc_mapper")

# Read MFC data
with open('/Users/dan.maguire/Downloads/WMT Stores/gopuff_mfc_data.json', 'r') as f:
    mfc_data = json.load(f)

print(f'Geocoding {len(mfc_data)} MFC locations...\n')

geocoded = 0
failed = []

for mfc in mfc_data:
    # Use zip code for geocoding
    address = f"{mfc['zip']}, USA"
    print(f"Geocoding: {mfc['name']}")
    print(f"  Zip: {mfc['zip']}")
    
    try:
        location = geolocator.geocode(address, timeout=10)
        
        if location:
            mfc['lat'] = location.latitude
            mfc['lon'] = location.longitude
            print(f"  ✓ Found: {location.latitude}, {location.longitude}")
            geocoded += 1
        else:
            print(f"  ✗ Not found")
            mfc['lat'] = 0.0
            mfc['lon'] = 0.0
            failed.append(mfc)
        
        # Be nice to the geocoding service
        time.sleep(1)
        
    except (GeocoderTimedOut, GeocoderServiceError) as e:
        print(f"  ✗ Error: {e}")
        mfc['lat'] = 0.0
        mfc['lon'] = 0.0
        failed.append(mfc)
        time.sleep(2)

print(f'\n\nGeocoding complete:')
print(f'  Successfully geocoded: {geocoded}')
print(f'  Failed: {len(failed)}')

if failed:
    print(f'\nFirst 10 failed locations:')
    for mfc in failed[:10]:
        print(f"  {mfc['name']} - {mfc['zip']}")

# Save geocoded data
with open('/Users/dan.maguire/Downloads/WMT Stores/gopuff_mfc_geocoded.json', 'w') as f:
    json.dump(mfc_data, f, indent=2)

print('\n✓ Saved geocoded MFC data to gopuff_mfc_geocoded.json')
