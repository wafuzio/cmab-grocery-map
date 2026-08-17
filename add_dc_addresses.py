import json
from geopy.geocoders import Nominatim
import time

# Load DC data
with open('/Users/dan.maguire/Downloads/WMT Stores/gopuff_dc_enhanced.json', 'r') as f:
    dc_data = json.load(f)

# Initialize geocoder
geolocator = Nominatim(user_agent='gopuff_dc_address_lookup', timeout=10)

print(f'Adding street addresses to {len(dc_data)} DC locations via reverse geocoding...')
print('This will take approximately 6-7 minutes (1 second per location for rate limiting)\n')

success_count = 0
failed_count = 0

for i, dc in enumerate(dc_data):
    try:
        # Reverse geocode to get address
        location = geolocator.reverse(f"{dc['lat']}, {dc['lon']}", language='en')
        
        if location and location.raw.get('address'):
            addr = location.raw['address']
            
            # Build street address
            street_parts = []
            if 'house_number' in addr:
                street_parts.append(addr['house_number'])
            if 'road' in addr:
                street_parts.append(addr['road'])
            
            street_address = ' '.join(street_parts) if street_parts else ''
            
            # Get city, state, zip
            city = addr.get('city') or addr.get('town') or addr.get('village') or addr.get('municipality') or ''
            state = addr.get('state') or ''
            postcode = addr.get('postcode') or dc.get('zip', '')
            
            # Create full address
            if street_address:
                dc['address'] = f"{street_address}, {city}, {state} {postcode}".strip()
            else:
                dc['address'] = f"{city}, {state} {postcode}".strip()
            
            success_count += 1
            if (i + 1) % 10 == 0:
                print(f"Progress: {i + 1}/{len(dc_data)} - {success_count} successful, {failed_count} failed")
        else:
            dc['address'] = f"{dc.get('city', '')}, {dc.get('zip', '')}".strip()
            failed_count += 1
            
    except Exception as e:
        dc['address'] = f"{dc.get('city', '')}, {dc.get('zip', '')}".strip()
        failed_count += 1
        if (i + 1) % 10 == 0:
            print(f"Progress: {i + 1}/{len(dc_data)} - {success_count} successful, {failed_count} failed")
    
    # Rate limiting - 1 request per second
    time.sleep(1)

print(f'\n✓ Completed!')
print(f'  Success: {success_count} DCs with street addresses')
print(f'  Fallback: {failed_count} DCs with city/zip only')

# Save updated data
with open('/Users/dan.maguire/Downloads/WMT Stores/gopuff_dc_enhanced.json', 'w') as f:
    json.dump(dc_data, f, indent=2)

print(f'\n✓ Saved to gopuff_dc_enhanced.json')
print(f'\nSample DC with address:')
print(json.dumps(dc_data[0], indent=2))
