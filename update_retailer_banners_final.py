import pandas as pd
import json
import re

# Read the promo Excel file to get store numbers by banner
print('Reading Excel file to identify retailer banners...')

# Crystal Creamery - Safeway stores
df_cc_safeway = pd.read_excel('2026 MilkPEP Neptune Supergirl Promo.xlsx', sheet_name='Crystal Creamery - Safeway', header=1)
safeway_stores = []
if 'Name' in df_cc_safeway.columns:
    for name in df_cc_safeway['Name'].dropna():
        match = re.search(r'#?(\d{3,4})', str(name))
        if match:
            safeway_stores.append(int(match.group(1)))

print(f'Found {len(safeway_stores)} Safeway stores (Crystal Creamery)')

# Hollandia - Albertsons/Vons stores
df_holl_alb = pd.read_excel('2026 MilkPEP Neptune Supergirl Promo.xlsx', sheet_name='Hollandia - Albertsons', header=1)
hollandia_albertsons = []
hollandia_vons = []

for col in df_holl_alb.columns:
    for val in df_holl_alb[col].dropna():
        val_str = str(val)
        if 'Albertsons #' in val_str:
            match = re.search(r'#(\d+)', val_str)
            if match:
                hollandia_albertsons.append(int(match.group(1)))
        elif 'Vons #' in val_str:
            match = re.search(r'#(\d+)', val_str)
            if match:
                hollandia_vons.append(int(match.group(1)))

print(f'Found {len(hollandia_albertsons)} Albertsons stores (Hollandia)')
print(f'Found {len(hollandia_vons)} Vons stores (Hollandia)')

# Now update the HTML file
print('\nReading Processor_Map.html...')
with open('/Users/dan.maguire/Downloads/WMT Stores/Processor_Map.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract STORES array
match = re.search(r'const STORES = (\[.*?\]);', content, re.DOTALL)
if match:
    stores_json = match.group(1)
    stores = json.loads(stores_json)
    
    print(f'Total stores in map: {len(stores)}')
    
    # Convert store number lists to strings with zero-padding for comparison
    safeway_stores_str = [str(s).zfill(4) for s in safeway_stores]
    hollandia_albertsons_str = [str(s).zfill(4) for s in hollandia_albertsons]
    hollandia_vons_str = [str(s).zfill(4) for s in hollandia_vons]
    
    # Update retailer names based on store numbers
    updated_safeway = 0
    updated_albertsons = 0
    updated_vons = 0
    
    for store in stores:
        sn = str(store['sn'])  # Store number as string
        
        # Check if this store should be Safeway
        if sn in safeway_stores_str:
            store['retailer'] = 'Safeway'
            updated_safeway += 1
        # Check if this store should be Vons (Hollandia)
        elif sn in hollandia_vons_str:
            store['retailer'] = 'Vons'
            updated_vons += 1
        # Check if this store should be Albertsons (Hollandia)
        elif sn in hollandia_albertsons_str:
            store['retailer'] = 'Albertsons'
            updated_albertsons += 1
    
    print(f'\nUpdated {updated_safeway} stores to Safeway')
    print(f'Updated {updated_albertsons} stores to Albertsons')
    print(f'Updated {updated_vons} stores to Vons')
    
    # Show final retailer distribution
    retailer_counts = {}
    for store in stores:
        ret = store['retailer']
        retailer_counts[ret] = retailer_counts.get(ret, 0) + 1
    
    print('\nFinal retailer distribution:')
    for retailer in sorted(retailer_counts.keys()):
        print(f'  {retailer}: {retailer_counts[retailer]} stores')
    
    # Convert back to JSON
    new_stores_json = json.dumps(stores, separators=(',', ':'))
    
    # Replace in content
    new_content = content.replace(match.group(0), f'const STORES = {new_stores_json};')
    
    # Write back
    with open('/Users/dan.maguire/Downloads/WMT Stores/Processor_Map.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print('\n✓ Retailer banners updated successfully')
else:
    print('ERROR: Could not find STORES array in HTML file')
