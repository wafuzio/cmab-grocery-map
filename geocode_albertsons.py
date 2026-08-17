import json
import time
import requests
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

geocoded_stores = []
failed = []
cache = {}

for i, store in enumerate(stores):
    if i % 100 == 0:
        print(f"Progress: {i}/{len(stores)}")
    
    # Build query
    query = f"{store['address']}, {store['city']}, {store['state']} {store['zip']}"
    
    # Check cache
    if query in cache:
        lat, lon = cache[query]
    else:
        # Use Nominatim geocoding
        try:
            url = f"https://nominatim.openstreetmap.org/search?q={requests.utils.quote(query)}&format=json&limit=1"
            headers = {'User-Agent': 'MilkPEP Store Mapper'}
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    lat = float(data[0]['lat'])
                    lon = float(data[0]['lon'])
                    cache[query] = (lat, lon)
                    time.sleep(1)  # Rate limiting
                else:
                    failed.append(store)
                    continue
            else:
                failed.append(store)
                continue
        except Exception as e:
            print(f"Error geocoding {query}: {e}")
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
        'lat': lat,
        'lon': lon,
        'cnt': 1,
        'retailer': store['retailer'],
        'processor': store['processor'],
        'region': region
    })

print(f"\nGeocoded: {len(geocoded_stores)}")
print(f"Failed: {len(failed)}")

# Save results
with open('/Users/dan.maguire/Downloads/WMT Stores/albertsons_geocoded.json', 'w') as f:
    json.dump(geocoded_stores, indent=2, fp=f)

if failed:
    with open('/Users/dan.maguire/Downloads/WMT Stores/albertsons_failed.json', 'w') as f:
        json.dump(failed, indent=2, fp=f)

print("\nSaved to albertsons_geocoded.json")
print(f"\nSample geocoded stores:")
for store in geocoded_stores[:3]:
    print(f"  {store['retailer']} #{store['sn']} - {store['city']}, {store['state']} ({store['lat']}, {store['lon']})")
