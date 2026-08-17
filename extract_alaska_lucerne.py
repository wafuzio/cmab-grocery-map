import pandas as pd
import re
import json

# Read Excel file
excel_path = '/Users/dan.maguire/Downloads/WMT Stores/2026 MilkPEP Neptune Supergirl Promo.xlsx'

# Read Lucerne sheet with correct header
df = pd.read_excel(excel_path, sheet_name='Lucerne', header=0)

# Filter for Alaska stores only (ST column contains state)
alaska_df = df[df['ST'] == 'AK'].copy()

print(f'Total Alaska Lucerne stores found: {len(alaska_df)}')

# Extract store data
stores = []
for _, row in alaska_df.iterrows():
    # Extract store number from Facility # column
    store_num_raw = str(row['Facility #'])
    
    # Try to extract numeric store number
    match = re.search(r'\d+', store_num_raw)
    if match:
        store_num = match.group(0)
    else:
        print(f'Warning: Could not extract store number from: {store_num_raw}')
        continue
    
    # Get retailer/banner
    retailer = str(row['Banner']).strip() if pd.notna(row['Banner']) else ''
    
    # Get division for region mapping
    division = str(row['Division']).strip() if pd.notna(row['Division']) else ''
    
    # Map division to region (Alaska is typically West)
    region_map = {
        'Denver': 'West',
        'Portland': 'West',
        'Northern California': 'West',
        'Southern California': 'West',
        'Intermountain': 'West',
        'Southwest': 'West',
        'Eastern': 'Northeast',
        'Albertsons': 'West'
    }
    region = region_map.get(division, 'West')
    
    # Get lat/lon if available
    lat = float(row['Latitude']) if 'Latitude' in row and pd.notna(row['Latitude']) else 0.0
    lon = float(row['Longitude']) if 'Longitude' in row and pd.notna(row['Longitude']) else 0.0
    
    store = {
        'sn': store_num,
        'addr': str(row['Street Address']).strip() if pd.notna(row['Street Address']) else '',
        'city': str(row['City']).strip() if pd.notna(row['City']) else '',
        'state': 'AK',
        'zip': str(int(row['ZIP'])) if pd.notna(row['ZIP']) else '',
        'lat': lat,
        'lon': lon,
        'processor': 'Lucerne',
        'retailer': retailer,
        'holding_co': 'Albertsons Companies',
        'region': region
    }
    
    stores.append(store)

print(f'\nExtracted {len(stores)} Alaska Lucerne stores')

# Show sample
if stores:
    print('\nSample stores:')
    for store in stores[:3]:
        print(f"  {store['retailer']} #{store['sn']} - {store['city']}, AK")

# Save to JSON
with open('/Users/dan.maguire/Downloads/WMT Stores/alaska_lucerne_stores.json', 'w') as f:
    json.dump(stores, f, indent=2)

print(f'\n✓ Saved to alaska_lucerne_stores.json')
