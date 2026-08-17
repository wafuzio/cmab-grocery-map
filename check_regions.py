import json
import re

with open('/Users/dan.maguire/Downloads/WMT Stores/WMT Store Map.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract STORES array
match = re.search(r'const STORES = (\[.*?\]);', content, re.DOTALL)
if match:
    stores_json = match.group(1)
    stores = json.loads(stores_json)
    
    print(f'Total stores: {len(stores)}')
    
    # Check for missing or undefined regions
    missing_region = []
    regions = {}
    
    for s in stores:
        region = s.get('region')
        if not region or region == 'undefined' or region == '':
            missing_region.append(s)
        else:
            if region not in regions:
                regions[region] = 0
            regions[region] += 1
    
    print(f'\nStores with missing/undefined region: {len(missing_region)}')
    if missing_region:
        print('\nFirst 10 stores with missing region:')
        for s in missing_region[:10]:
            print(f'  {s["retailer"]} #{s["sn"]} - {s["city"]}, {s["state"]} - region: {s.get("region", "MISSING KEY")}')
    
    print(f'\nValid regions found:')
    for region, count in sorted(regions.items()):
        print(f'  {region}: {count} stores')
    
    print(f'\nTotal stores with valid regions: {sum(regions.values())}')
    print(f'Total stores missing regions: {len(missing_region)}')
    print(f'Sum check: {sum(regions.values()) + len(missing_region)} should equal {len(stores)}')
