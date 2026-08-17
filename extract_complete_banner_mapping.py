import pandas as pd
import re

# Dictionary to store all store-to-banner mappings
store_to_banner = {}

print('Extracting store-to-banner mappings from Excel tabs...\n')

# 1. Lucerne tab - has Albertsons, Safeway, and Vons stores
print('Processing Lucerne tab...')
df_lucerne = pd.read_excel('2026 MilkPEP Neptune Supergirl Promo.xlsx', sheet_name='Lucerne', header=1)
banner_col_idx = 2  # Third column has the banner
store_col_idx = 5   # Sixth column has store info

for idx, row in df_lucerne.iterrows():
    banner = str(row.iloc[banner_col_idx]).strip()
    store_info = str(row.iloc[store_col_idx])
    
    # Extract 4-digit store number
    match = re.search(r'(\d{4})', store_info)
    if match and banner in ['Safeway', 'Albertsons', 'Vons']:
        store_num = match.group(1)
        store_to_banner[store_num] = banner

print(f'  Found {len(store_to_banner)} stores from Lucerne tab')

# 2. Crystal Creamery - Safeway tab
print('Processing Crystal Creamery - Safeway tab...')
df_cc_safeway = pd.read_excel('2026 MilkPEP Neptune Supergirl Promo.xlsx', sheet_name='Crystal Creamery - Safeway', header=1)
if 'Name' in df_cc_safeway.columns:
    for name in df_cc_safeway['Name'].dropna():
        match = re.search(r'#?(\d{3,4})', str(name))
        if match:
            store_num = match.group(1).zfill(4)
            store_to_banner[store_num] = 'Safeway'

print(f'  Total stores after Crystal Creamery - Safeway: {len(store_to_banner)}')

# 3. Hollandia - Albertsons tab
print('Processing Hollandia - Albertsons tab...')
df_holl_alb = pd.read_excel('2026 MilkPEP Neptune Supergirl Promo.xlsx', sheet_name='Hollandia - Albertsons', header=1)
for col in df_holl_alb.columns:
    for val in df_holl_alb[col].dropna():
        val_str = str(val)
        if 'Albertsons #' in val_str:
            match = re.search(r'#(\d+)', val_str)
            if match:
                store_num = match.group(1).zfill(4)
                store_to_banner[store_num] = 'Albertsons'
        elif 'Vons #' in val_str:
            match = re.search(r'#(\d+)', val_str)
            if match:
                store_num = match.group(1).zfill(4)
                store_to_banner[store_num] = 'Vons'

print(f'  Total stores after Hollandia - Albertsons: {len(store_to_banner)}')

# Count by banner
banner_counts = {}
for banner in store_to_banner.values():
    banner_counts[banner] = banner_counts.get(banner, 0) + 1

print('\nFinal banner distribution from Excel:')
for banner in sorted(banner_counts.keys()):
    print(f'  {banner}: {banner_counts[banner]} stores')

# Check if store 1825 is in the mapping
if '1825' in store_to_banner:
    print(f'\nStore #1825 should be: {store_to_banner["1825"]}')
else:
    print('\nStore #1825 NOT found in Excel tabs - will remain as current retailer')

# Save to JSON
import json
with open('complete_banner_mapping.json', 'w') as f:
    json.dump(store_to_banner, f, indent=2)

print('\n✓ Saved complete mapping to complete_banner_mapping.json')
