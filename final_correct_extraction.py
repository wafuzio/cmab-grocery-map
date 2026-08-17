import pandas as pd
import json
import re

print('='*80)
print('FINAL CORRECTED EXCEL EXTRACTION')
print('='*80)

expected_assignments = {}

# 1. Maola - Walmart tab
print('\n1. Processing Maola - Walmart tab...')
df_maola = pd.read_excel('2026 MilkPEP Neptune Supergirl Promo.xlsx', sheet_name='Maola - Walmart', header=0)
# First column (after header row A1) contains store numbers starting from A2
maola_stores = []
for val in df_maola.iloc[:, 0].dropna():
    sn = str(int(val)).zfill(4)
    expected_assignments[sn] = {'retailer': 'Walmart', 'processor': 'Maola'}
    maola_stores.append(sn)
print(f'   Found {len(maola_stores)} stores')
print(f'   First store: {maola_stores[0]}, Last store: {maola_stores[-1]}')

# 2. Sarah Farms - Walmart tab
print('\n2. Processing Sarah Farms - Walmart tab...')
df_sarah = pd.read_excel('2026 MilkPEP Neptune Supergirl Promo.xlsx', sheet_name='Sarah Farms - Walmart', header=0)
sarah_stores = []
for val in df_sarah.iloc[:, 0].dropna():
    # Handle both numeric and text formats
    match = re.search(r'(\d{4})', str(val))
    if match:
        sn = match.group(1)
        expected_assignments[sn] = {'retailer': 'Walmart', 'processor': 'Sarah Farms'}
        sarah_stores.append(sn)
print(f'   Found {len(sarah_stores)} stores')

# 3. Crystal Creamery - WMT tab
print('\n3. Processing Crystal Creamery - WMT tab...')
df_cc_wmt = pd.read_excel('2026 MilkPEP Neptune Supergirl Promo.xlsx', sheet_name='Crystal Creamery - WMT', header=0)
cc_wmt_stores = []
for val in df_cc_wmt.iloc[:, 0].dropna():
    match = re.search(r'(\d{4})', str(val))
    if match:
        sn = match.group(1)
        expected_assignments[sn] = {'retailer': 'Walmart', 'processor': 'Crystal Creamery'}
        cc_wmt_stores.append(sn)
print(f'   Found {len(cc_wmt_stores)} stores')

# 4. Crystal Creamery - Safeway tab
print('\n4. Processing Crystal Creamery - Safeway tab...')
df_cc_safeway = pd.read_excel('2026 MilkPEP Neptune Supergirl Promo.xlsx', sheet_name='Crystal Creamery - Safeway', header=1)
# The 'Name' column has store names like "SAFEWAY #2695 ROSEVILLE"
cc_safeway_stores = []
name_col = df_cc_safeway.columns[1]  # Second column is 'Name'
for name in df_cc_safeway[name_col].dropna():
    match = re.search(r'#(\d{3,4})', str(name))
    if match:
        sn = match.group(1).zfill(4)
        expected_assignments[sn] = {'retailer': 'Safeway', 'processor': 'Crystal Creamery'}
        cc_safeway_stores.append(sn)
print(f'   Found {len(cc_safeway_stores)} stores')

# 5. Hollandia - Walmart tab
print('\n5. Processing Hollandia - Walmart tab...')
df_holl_wmt = pd.read_excel('2026 MilkPEP Neptune Supergirl Promo.xlsx', sheet_name='Hollandia - Walmart', header=0)
holl_wmt_stores = []
# Store # is in the second column (index 1)
for val in df_holl_wmt['Store #'].dropna():
    sn = str(int(val)).zfill(4)
    expected_assignments[sn] = {'retailer': 'Walmart', 'processor': 'Hollandia'}
    holl_wmt_stores.append(sn)
print(f'   Found {len(holl_wmt_stores)} stores')

# 6. Hollandia - Albertsons tab
print('\n6. Processing Hollandia - Albertsons tab...')
df_holl_alb = pd.read_excel('2026 MilkPEP Neptune Supergirl Promo.xlsx', sheet_name='Hollandia - Albertsons', header=0)
holl_alb_count = 0
holl_vons_count = 0
for col in df_holl_alb.columns:
    for val in df_holl_alb[col].dropna():
        val_str = str(val)
        if 'Albertsons #' in val_str:
            match = re.search(r'#(\d+)', val_str)
            if match:
                sn = match.group(1).zfill(4)
                expected_assignments[sn] = {'retailer': 'Albertsons', 'processor': 'Hollandia'}
                holl_alb_count += 1
        elif 'Vons #' in val_str:
            match = re.search(r'#(\d+)', val_str)
            if match:
                sn = match.group(1).zfill(4)
                expected_assignments[sn] = {'retailer': 'Vons', 'processor': 'Hollandia'}
                holl_vons_count += 1
print(f'   Found {holl_alb_count} Albertsons stores')
print(f'   Found {holl_vons_count} Vons stores')

# 7. Lucerne tab - ALL RETAILERS
print('\n7. Processing Lucerne tab (ALL retailers)...')
df_lucerne = pd.read_excel('2026 MilkPEP Neptune Supergirl Promo.xlsx', sheet_name='Lucerne', header=0)
# Find banner and store number columns
banner_col_idx = 2
store_col_idx = 5

lucerne_counts = {}
for idx, row in df_lucerne.iterrows():
    banner = str(row.iloc[banner_col_idx]).strip()
    store_info = str(row.iloc[store_col_idx])
    
    match = re.search(r'(\d{4})', store_info)
    if match and banner not in ['nan', '']:
        sn = match.group(1)
        expected_assignments[sn] = {'retailer': banner, 'processor': 'Lucerne'}
        lucerne_counts[banner] = lucerne_counts.get(banner, 0) + 1

print('   Lucerne processor stores by retailer:')
for retailer in sorted(lucerne_counts.keys()):
    print(f'     {retailer}: {lucerne_counts[retailer]} stores')

print(f'\n{"="*80}')
print(f'TOTAL EXPECTED STORES FROM EXCEL: {len(expected_assignments)}')
print(f'{"="*80}')

# Summary by retailer and processor
print('\nExpected distribution:')
retailer_proc_counts = {}
for sn, data in expected_assignments.items():
    key = f"{data['retailer']} / {data['processor']}"
    retailer_proc_counts[key] = retailer_proc_counts.get(key, 0) + 1

for combo in sorted(retailer_proc_counts.keys()):
    print(f'  {combo}: {retailer_proc_counts[combo]} stores')

# Save
with open('expected_assignments_final.json', 'w') as f:
    json.dump(expected_assignments, f, indent=2)

print('\n✓ Final corrected assignments saved to expected_assignments_final.json')
