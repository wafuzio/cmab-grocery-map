import json
import requests
import os
from collections import Counter

# Read delivery zip codes
with open('/Users/dan.maguire/Downloads/WMT Stores/gopuff_delivery_data.json', 'r') as f:
    delivery_data = json.load(f)

# Get unique states
states = Counter(d['state'] for d in delivery_data)
print(f'States needing zip code data: {len(states)}')
print(f'States: {sorted(states.keys())}')

# State name mapping for GitHub repo
state_names = {
    'AL': 'alabama', 'AZ': 'arizona', 'CA': 'california', 'CO': 'colorado',
    'CT': 'connecticut', 'DE': 'delaware', 'DC': 'district_of_columbia',
    'FL': 'florida', 'GA': 'georgia', 'IA': 'iowa', 'IL': 'illinois',
    'IN': 'indiana', 'KS': 'kansas', 'KY': 'kentucky', 'LA': 'louisiana',
    'MA': 'massachusetts', 'MD': 'maryland', 'ME': 'maine', 'MI': 'michigan',
    'MN': 'minnesota', 'MO': 'missouri', 'NC': 'north_carolina', 'NE': 'nebraska',
    'NH': 'new_hampshire', 'NJ': 'new_jersey', 'NM': 'new_mexico', 'NV': 'nevada',
    'NY': 'new_york', 'OH': 'ohio', 'OK': 'oklahoma', 'OR': 'oregon',
    'PA': 'pennsylvania', 'RI': 'rhode_island', 'SC': 'south_carolina',
    'TN': 'tennessee', 'TX': 'texas', 'VA': 'virginia', 'WA': 'washington',
    'WI': 'wisconsin', 'WV': 'west_virginia'
}

# Get all delivery zip codes
delivery_zips = set(d['zip'] for d in delivery_data)
print(f'\nTotal unique delivery zip codes: {len(delivery_zips)}')

# Create a strategy: download state files and filter to only our zips
print('\nDownloading zip code boundaries for states with delivery coverage...')
print('This may take a few minutes...\n')

all_zip_features = []
downloaded_count = 0

for state_abbr in sorted(states.keys()):
    if state_abbr not in state_names:
        print(f'Skipping {state_abbr} - no mapping')
        continue
    
    state_name = state_names[state_abbr]
    state_zips = [d['zip'] for d in delivery_data if d['state'] == state_abbr]
    
    # GitHub raw URL for the state's zip code GeoJSON
    url = f'https://raw.githubusercontent.com/OpenDataDE/State-zip-code-GeoJSON/master/{state_abbr.lower()}_{state_name}_zip_codes_geo.min.json'
    
    try:
        print(f'Downloading {state_abbr} ({len(state_zips)} delivery zips)... ', end='', flush=True)
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            state_geojson = response.json()
            
            # Filter to only include zips in our delivery list
            filtered_features = []
            for feature in state_geojson.get('features', []):
                zip_code = feature['properties'].get('ZCTA5CE10') or feature['properties'].get('GEOID10')
                if zip_code in delivery_zips:
                    filtered_features.append(feature)
            
            all_zip_features.extend(filtered_features)
            downloaded_count += 1
            print(f'✓ Found {len(filtered_features)} matching zips')
        else:
            print(f'✗ HTTP {response.status_code}')
    except Exception as e:
        print(f'✗ Error: {str(e)}')

print(f'\n✓ Downloaded {downloaded_count} states')
print(f'✓ Total zip code polygons: {len(all_zip_features)}')

# Create final GeoJSON
final_geojson = {
    'type': 'FeatureCollection',
    'features': all_zip_features
}

# Save to file
output_file = '/Users/dan.maguire/Downloads/WMT Stores/gopuff_delivery_zip_boundaries.json'
with open(output_file, 'w') as f:
    json.dump(final_geojson, f, separators=(',', ':'))

file_size = os.path.getsize(output_file) / (1024 * 1024)
print(f'\n✓ Saved to gopuff_delivery_zip_boundaries.json ({file_size:.1f} MB)')
print(f'✓ Ready to use in the map!')
