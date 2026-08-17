import json
import re

# Load the complete banner mapping
with open('complete_banner_mapping.json', 'r') as f:
    store_to_banner = json.load(f)

print(f'Loaded mapping for {len(store_to_banner)} stores')

# Read the HTML file
with open('Processor_Map.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract STORES array
match = re.search(r'const STORES = (\[.*?\]);', content, re.DOTALL)
if match:
    stores_json = match.group(1)
    stores = json.loads(stores_json)
    
    print(f'Total stores in map: {len(stores)}')
    
    # Update retailer names based on complete mapping
    # ONLY update stores that are currently labeled as Albertsons (actual ABSCO stores)
    updated_count = 0
    not_in_mapping = 0
    
    for store in stores:
        sn = str(store['sn'])
        current_retailer = store['retailer']
        
        # Only process stores currently labeled as Albertsons, Safeway, or Vons
        # Do NOT change Walmart stores
        if current_retailer in ['Albertsons', 'Safeway', 'Vons']:
            # Check if this store is in our ABSCO banner mapping
            if sn in store_to_banner:
                new_banner = store_to_banner[sn]
                if current_retailer != new_banner:
                    store['retailer'] = new_banner
                    updated_count += 1
            else:
                # ABSCO store not in mapping - keep as Albertsons by default
                not_in_mapping += 1
    
    print(f'\nUpdated {updated_count} stores to correct banners')
    print(f'{not_in_mapping} ABSCO stores not in Excel mapping (kept current retailer)')
    
    # Show final retailer distribution
    retailer_counts = {}
    processor_by_retailer = {}
    
    for store in stores:
        ret = store['retailer']
        proc = store['processor']
        
        retailer_counts[ret] = retailer_counts.get(ret, 0) + 1
        
        if ret not in processor_by_retailer:
            processor_by_retailer[ret] = {}
        processor_by_retailer[ret][proc] = processor_by_retailer[ret].get(proc, 0) + 1
    
    print('\nFinal retailer distribution:')
    for retailer in sorted(retailer_counts.keys()):
        print(f'  {retailer}: {retailer_counts[retailer]} stores')
        if retailer in processor_by_retailer:
            for proc, count in sorted(processor_by_retailer[retailer].items()):
                print(f'    - {proc}: {count}')
    
    # Verify store #1825
    store_1825 = next((s for s in stores if s['sn'] == '1825'), None)
    if store_1825:
        print(f'\n✓ Store #1825 verification:')
        print(f'  Retailer: {store_1825["retailer"]}')
        print(f'  Processor: {store_1825["processor"]}')
        print(f'  Location: {store_1825["city"]}, {store_1825["state"]}')
    
    # Convert back to JSON
    new_stores_json = json.dumps(stores, separators=(',', ':'))
    
    # Replace in content
    new_content = content.replace(match.group(0), f'const STORES = {new_stores_json};')
    
    # Write back
    with open('Processor_Map.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print('\n✓ All retailer banners updated successfully')
else:
    print('ERROR: Could not find STORES array in HTML file')
