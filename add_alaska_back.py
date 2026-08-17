import json
import re
import urllib.request

# Download Alaska geoJSON from a reliable source
url = 'https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json'
with urllib.request.urlopen(url) as response:
    data = json.loads(response.read())
    
# Find Alaska feature (id: '02' or name: 'Alaska')
alaska = None
for feature in data['features']:
    if feature.get('id') == '02' or feature.get('properties', {}).get('name') == 'Alaska':
        alaska = feature
        break

if not alaska:
    print('ERROR: Alaska not found in source data')
    exit(1)

# Read the HTML file
with open('/Users/dan.maguire/Downloads/WMT Stores/Processor_Map.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find US_STATES and extract it
match = re.search(r'const US_STATES = (\{.*?\});', content, re.DOTALL)
if match:
    us_states_json = match.group(1)
    us_states = json.loads(us_states_json)
    
    # Check if Alaska already exists
    has_alaska = any(f.get('id') == '02' or f.get('properties', {}).get('name') == 'Alaska' 
                     for f in us_states['features'])
    
    if has_alaska:
        print('Alaska already exists in US_STATES')
    else:
        # Add Alaska to features (insert after Alabama which is first)
        us_states['features'].insert(1, alaska)
        
        print(f'Total states before: {len(json.loads(us_states_json)["features"])}')
        print(f'Total states after: {len(us_states["features"])}')
        
        # Convert back to compact JSON
        new_us_states_json = json.dumps(us_states, separators=(',', ':'))
        
        # Replace in content
        new_content = content.replace(match.group(0), f'const US_STATES = {new_us_states_json};')
        
        # Write back
        with open('/Users/dan.maguire/Downloads/WMT Stores/Processor_Map.html', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print('✓ Alaska added to US_STATES')
else:
    print('ERROR: Could not find US_STATES in HTML')
