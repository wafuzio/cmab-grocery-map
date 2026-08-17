import pandas as pd
import json
import re

print('='*80)
print('COMPLETE AUDIT - ALL TABS AND ALL RETAILERS')
print('='*80)

# Dictionary to store expected assignments from Excel
expected_assignments = {}

# 1. Extract from Maola - Walmart tab
print('\n1. Processing Maola - Walmart tab...')
df_maola = pd.read_excel('2026 MilkPEP Neptune Supergirl Promo.xlsx', sheet_name='Maola - Walmart', header=1)
maola_count = 0
for col in df_maola.columns:
    for val in df_maola[col].dropna():
        match = re.search(r'(\d{4})', str(val))
        if match:
            store_num = match.group(1)
            expected_assignments[store_num] = {'retailer': 'Walmart', 'processor': 'Maola'}
            maola_count += 1
print(f'   Found {maola_count} Walmart stores with Maola processor')

# 2. Extract from Sarah Farms - Walmart tab
print('\n2. Processing Sarah Farms - Walmart tab...')
df_sarah = pd.read_excel('2026 MilkPEP Neptune Supergirl Promo.xlsx', sheet_name='Sarah Farms - Walmart', header=1)
sarah_count = 0
for col in df_sarah.columns:
    for val in df_sarah[col].dropna():
        match = re.search(r'(\d{4})', str(val))
        if match:
            store_num = match.group(1)
            expected_assignments[store_num] = {'retailer': 'Walmart', 'processor': 'Sarah Farms'}
            sarah_count += 1
print(f'   Found {sarah_count} Walmart stores with Sarah Farms processor')

# 3. Extract from Crystal Creamery - WMT tab
print('\n3. Processing Crystal Creamery - WMT tab...')
df_cc_wmt = pd.read_excel('2026 MilkPEP Neptune Supergirl Promo.xlsx', sheet_name='Crystal Creamery - WMT', header=1)
cc_wmt_count = 0
for col in df_cc_wmt.columns:
    for val in df_cc_wmt[col].dropna():
        match = re.search(r'(\d{4})', str(val))
        if match:
            store_num = match.group(1)
            expected_assignments[store_num] = {'retailer': 'Walmart', 'processor': 'Crystal Creamery'}
            cc_wmt_count += 1
print(f'   Found {cc_wmt_count} Walmart stores with Crystal Creamery processor')

# 4. Extract from Crystal Creamery - Safeway tab
print('\n4. Processing Crystal Creamery - Safeway tab...')
df_cc_safeway = pd.read_excel('2026 MilkPEP Neptune Supergirl Promo.xlsx', sheet_name='Crystal Creamery - Safeway', header=1)
cc_safeway_count = 0
if 'Name' in df_cc_safeway.columns:
    for name in df_cc_safeway['Name'].dropna():
        match = re.search(r'#?(\d{3,4})', str(name))
        if match:
            store_num = match.group(1).zfill(4)
            expected_assignments[store_num] = {'retailer': 'Safeway', 'processor': 'Crystal Creamery'}
            cc_safeway_count += 1
print(f'   Found {cc_safeway_count} Safeway stores with Crystal Creamery processor')

# 5. Extract from Hollandia - Walmart tab
print('\n5. Processing Hollandia - Walmart tab...')
df_holl_wmt = pd.read_excel('2026 MilkPEP Neptune Supergirl Promo.xlsx', sheet_name='Hollandia - Walmart', header=1)
holl_wmt_count = 0
for col in df_holl_wmt.columns:
    for val in df_holl_wmt[col].dropna():
        match = re.search(r'(\d{4})', str(val))
        if match:
            store_num = match.group(1)
            expected_assignments[store_num] = {'retailer': 'Walmart', 'processor': 'Hollandia'}
            holl_wmt_count += 1
print(f'   Found {holl_wmt_count} Walmart stores with Hollandia processor')

# 6. Extract from Hollandia - Albertsons tab
print('\n6. Processing Hollandia - Albertsons tab...')
df_holl_alb = pd.read_excel('2026 MilkPEP Neptune Supergirl Promo.xlsx', sheet_name='Hollandia - Albertsons', header=1)
holl_alb_count = 0
holl_vons_count = 0
for col in df_holl_alb.columns:
    for val in df_holl_alb[col].dropna():
        val_str = str(val)
        if 'Albertsons #' in val_str:
            match = re.search(r'#(\d+)', val_str)
            if match:
                store_num = match.group(1).zfill(4)
                expected_assignments[store_num] = {'retailer': 'Albertsons', 'processor': 'Hollandia'}
                holl_alb_count += 1
        elif 'Vons #' in val_str:
            match = re.search(r'#(\d+)', val_str)
            if match:
                store_num = match.group(1).zfill(4)
                expected_assignments[store_num] = {'retailer': 'Vons', 'processor': 'Hollandia'}
                holl_vons_count += 1
print(f'   Found {holl_alb_count} Albertsons stores with Hollandia processor')
print(f'   Found {holl_vons_count} Vons stores with Hollandia processor')

# 7. Extract from Lucerne tab - ALL RETAILERS
print('\n7. Processing Lucerne tab (ALL retailers)...')
df_lucerne = pd.read_excel('2026 MilkPEP Neptune Supergirl Promo.xlsx', sheet_name='Lucerne', header=1)
banner_col_idx = 2
store_col_idx = 5

# Count by retailer
lucerne_counts = {}

for idx, row in df_lucerne.iterrows():
    banner = str(row.iloc[banner_col_idx]).strip()
    store_info = str(row.iloc[store_col_idx])
    
    match = re.search(r'(\d{4})', store_info)
    if match and banner not in ['nan', '']:
        store_num = match.group(1)
        expected_assignments[store_num] = {'retailer': banner, 'processor': 'Lucerne'}
        lucerne_counts[banner] = lucerne_counts.get(banner, 0) + 1

print('   Lucerne processor stores by retailer:')
for retailer in sorted(lucerne_counts.keys()):
    print(f'     {retailer}: {lucerne_counts[retailer]} stores')

print(f'\n{"="*80}')
print(f'TOTAL EXPECTED STORES FROM EXCEL: {len(expected_assignments)}')
print(f'{"="*80}')

# Save expected assignments for reference
with open('expected_assignments.json', 'w') as f:
    json.dump(expected_assignments, f, indent=2)

print('\n✓ Expected assignments saved to expected_assignments.json')
print(f'\nUnique retailers in Excel: {sorted(set(a["retailer"] for a in expected_assignments.values()))}')
print(f'Unique processors in Excel: {sorted(set(a["processor"] for a in expected_assignments.values()))}')
