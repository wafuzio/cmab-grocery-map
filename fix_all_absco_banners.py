import json
import re

# Load the banner mapping
with open('absco_banners.json', 'r') as f:
    stores_by_banner = json.load(f)

print('Loaded banner mapping:')
for banner, stores in stores_by_banner.items():
    print(f'  {banner}: {len(stores)} stores')

# Read the HTML file
with open('Processor_Map.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract STORES array
match = re.search(r'const STORES = (\[.*?\]);', content, re.DOTALL)
if match:
    stores_json = match.group(1)
    stores = json.loads(stores_json)
    
    print(f'\nTotal stores in map: {len(stores)}')
    
    # Update retailer names based on banner mapping
    updated_safeway = 0
    updated_albertsons = 0
    updated_vons = 0
    reverted_to_albertsons = 0
    
    for store in stores:
        sn = str(store['sn'])
        current_retailer = store['retailer']
        
        # Only update if currently labeled as Albertsons, Safeway, or Vons
        if current_retailer in ['Albertsons', 'Safeway', 'Vons']:
            # Check which banner this store should have
            if sn in stores_by_banner['Safeway']:
                if store['retailer'] != 'Safeway':
                    store['retailer'] = 'Safeway'
                    updated_safeway += 1
            elif sn in stores_by_banner['Vons']:
                if store['retailer'] != 'Vons':
                    store['retailer'] = 'Vons'
                    updated_vons += 1
            elif sn in stores_by_banner['Albertsons']:
                if store['retailer'] != 'Albertsons':
                    store['retailer'] = 'Albertsons'
                    updated_albertsons += 1
            else:
                # Store not in any banner list - revert to Albertsons as default
                if store['retailer'] != 'Albertsons':
                    store['retailer'] = 'Albertsons'
                    reverted_to_albertsons += 1
    
    print(f'\nUpdated {updated_safeway} stores to Safeway')
    print(f'Updated {updated_albertsons} stores to Albertsons')
    print(f'Updated {updated_vons} stores to Vons')
    print(f'Reverted {reverted_to_albertsons} stores to Albertsons (not in banner lists)')
    
    # Show final retailer distribution
    retailer_counts = {}
    for store in stores:
        ret = store['retailer']
        retailer_counts[ret] = retailer_counts.get(ret, 0) + 1
    
    print('\nFinal retailer distribution:')
    for retailer in sorted(retailer_counts.keys()):
        print(f'  {retailer}: {retailer_counts[retailer]} stores')
    
    # Verify store #1825
    store_1825 = next((s for s in stores if s['sn'] == '1825'), None)
    if store_1825:
        print(f'\nStore #1825 now labeled as: {store_1825["retailer"]}')
    
    # Convert back to JSON
    new_stores_json = json.dumps(stores, separators=(',', ':'))
    
    # Replace in content
    new_content = content.replace(match.group(0), f'const STORES = {new_stores_json};')
    
    # Write back
    with open('Processor_Map.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print('\n✓ All ABSCO retailer banners updated successfully')
else:
    print('ERROR: Could not find STORES array in HTML file')
