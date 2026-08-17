import pandas as pd
import re

# Read the Lucerne tab which has all ABSCO stores with their banners
df_lucerne = pd.read_excel('2026 MilkPEP Neptune Supergirl Promo.xlsx', sheet_name='Lucerne', header=1)

print('Lucerne tab columns:', df_lucerne.columns.tolist())
print(f'Total rows: {len(df_lucerne)}')

# The third column appears to be the banner name
# Let's identify which column has the banner and which has the store info
banner_col = df_lucerne.columns[2]  # 'Safeway' or 'Albertsons' etc
store_info_col = df_lucerne.columns[5]  # Store number like 'SS00008AS'

print(f'\nBanner column: {banner_col}')
print(f'Store info column: {store_info_col}')

# Extract store numbers by banner
stores_by_banner = {
    'Safeway': [],
    'Albertsons': [],
    'Vons': []
}

for idx, row in df_lucerne.iterrows():
    banner = row[banner_col]
    store_info = str(row[store_info_col])
    
    # Extract store number from formats like 'SS00008AS' or similar
    # Try to find 4-digit numbers
    match = re.search(r'(\d{4})', store_info)
    if match and banner in stores_by_banner:
        store_num = match.group(1)
        stores_by_banner[banner].append(store_num)

print('\nStores by banner:')
for banner, stores in stores_by_banner.items():
    print(f'  {banner}: {len(stores)} stores')
    print(f'    Sample store numbers: {stores[:10]}')

# Save to file for verification
import json
with open('absco_banners.json', 'w') as f:
    json.dump(stores_by_banner, f, indent=2)

print('\n✓ Saved banner mapping to absco_banners.json')
