import json
import time
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from collections import defaultdict

# Load the extracted stores
with open('/Users/dan.maguire/Downloads/WMT Stores/new_retailers.json', 'r') as f:
    stores = json.load(f)

print(f"Geocoding {len(stores)} Albertsons stores...")

# State to region mapping
STATE_TO_REGION = {
    'WA': 'Northwest', 'OR': 'Northwest', 'ID': 'Northwest', 'MT': 'Northwest', 'WY': 'Northwest',
    'CA': 'West', 'NV': 'West', 'UT': 'West', 'AZ': 'Southwest', 'NM': 'Southwest', 'CO': 'Southwest',
    'TX': 'Southwest', 'OK': 'Southwest', 'AR': 'Southwest', 'LA': 'Southwest',
    'ND': 'Midwest', 'SD': 'Midwest', 'NE': 'Midwest', 'KS': 'Midwest', 'MN': 'Midwest', 'IA': 'Midwest',
    'MO': 'Midwest', 'WI': 'Midwest', 'IL': 'Midwest', 'MI': 'Midwest', 'IN': 'Midwest', 'OH': 'Midwest',
    'KY': 'Southeast', 'TN': 'Southeast', 'MS': 'Southeast', 'AL': 'Southeast', 'GA': 'Southeast',
    'FL': 'Southeast', 'SC': 'Southeast', 'NC': 'Southeast', 'VA': 'Southeast', 'WV': 'Southeast',
    'MD': 'Northeast', 'DE': 'Northeast', 'PA': 'Northeast', 'NJ': 'Northeast', 'NY': 'Northeast',
    'CT': 'Northeast', 'RI': 'Northeast', 'MA': 'Northeast', 'VT': 'Northeast', 'NH': 'Northeast', 'ME': 'Northeast',
    'DC': 'Northeast', 'AK': 'West', 'HI': 'West'
}

# Initialize geocoder with rate limiting
geolocator = Nominatim(user_agent="MilkPEP_Store_Mapper_v1")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1.1)

geocoded_stores = []
failed = []

for i, store in enumerate(stores):
    if i % 50 == 0:
        print(f"Progress: {i}/{len(stores)} ({100*i//len(stores)}%)")
    
    # Build query
    query = f"{store['address']}, {store['city']}, {store['state']} {store['zip']}"
    
    try:
        location = geocode(query, timeout=10)
        
        if location:
            lat = location.latitude
            lon = location.longitude
        else:
            # Try without zip
            query2 = f"{store['address']}, {store['city']}, {store['state']}"
            location = geocode(query2, timeout=10)
            if location:
                lat = location.latitude
                lon = location.longitude
            else:
                print(f"  Failed: {query}")
                failed.append(store)
                continue
    except Exception as e:
        print(f"  Error geocoding {query}: {e}")
        failed.append(store)
        continue
    
    # Add region
    region = STATE_TO_REGION.get(store['state'], 'Unknown')
    
    geocoded_stores.append({
        'sn': store['store_num'],
        'addr': store['address'],
        'city': store['city'],
        'state': store['state'],
        'zip': store['zip'],
        'lat': round(lat, 7),
        'lon': round(lon, 7),
        'cnt': 1,
        'retailer': store['retailer'],
        'processor': store['processor'],
        'region': region
    })

print(f"\n✓ Geocoded: {len(geocoded_stores)}")
print(f"✗ Failed: {len(failed)}")

# Save results
with open('/Users/dan.maguire/Downloads/WMT Stores/albertsons_geocoded.json', 'w') as f:
    json.dump(geocoded_stores, indent=2, fp=f)

if failed:
    with open('/Users/dan.maguire/Downloads/WMT Stores/albertsons_failed.json', 'w') as f:
        json.dump(failed, indent=2, fp=f)
    print(f"\nFailed stores saved to albertsons_failed.json")

print("\n✓ Saved to albertsons_geocoded.json")
print(f"\nSample geocoded stores:")
for store in geocoded_stores[:5]:
    print(f"  {store['retailer']} #{store['sn']} - {store['processor']} - {store['city']}, {store['state']} ({store['lat']}, {store['lon']})")
