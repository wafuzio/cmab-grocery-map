import pandas as pd
import json
import re

print('='*80)
print('COMPLETE AUDIT OF STORE ASSIGNMENTS')
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

# 7. Extract from Lucerne tab
print('\n7. Processing Lucerne tab...')
df_lucerne = pd.read_excel('2026 MilkPEP Neptune Supergirl Promo.xlsx', sheet_name='Lucerne', header=1)
banner_col_idx = 2
store_col_idx = 5

lucerne_albertsons = 0
lucerne_safeway = 0
lucerne_vons = 0

for idx, row in df_lucerne.iterrows():
    banner = str(row.iloc[banner_col_idx]).strip()
    store_info = str(row.iloc[store_col_idx])
    
    match = re.search(r'(\d{4})', store_info)
    if match and banner in ['Safeway', 'Albertsons', 'Vons']:
        store_num = match.group(1)
        expected_assignments[store_num] = {'retailer': banner, 'processor': 'Lucerne'}
        if banner == 'Albertsons':
            lucerne_albertsons += 1
        elif banner == 'Safeway':
            lucerne_safeway += 1
        elif banner == 'Vons':
            lucerne_vons += 1

print(f'   Found {lucerne_albertsons} Albertsons stores with Lucerne processor')
print(f'   Found {lucerne_safeway} Safeway stores with Lucerne processor')
print(f'   Found {lucerne_vons} Vons stores with Lucerne processor')

print(f'\n{"="*80}')
print(f'TOTAL EXPECTED STORES FROM EXCEL: {len(expected_assignments)}')
print(f'{"="*80}')

# Now compare with current HTML data
print('\nReading current HTML store data...')
with open('Processor_Map.html', 'r', encoding='utf-8') as f:
    content = f.read()

match = re.search(r'const STORES = (\[.*?\]);', content, re.DOTALL)
if match:
    stores = json.loads(match.group(1))
    print(f'Total stores in HTML: {len(stores)}')
    
    # Compare each store
    mismatches = []
    missing_from_html = []
    extra_in_html = []
    
    # Check stores in HTML against expected
    for store in stores:
        sn = str(store['sn'])
        current_retailer = store['retailer']
        current_processor = store['processor']
        
        if sn in expected_assignments:
            expected = expected_assignments[sn]
            if current_retailer != expected['retailer'] or current_processor != expected['processor']:
                mismatches.append({
                    'sn': sn,
                    'current': f"{current_retailer} / {current_processor}",
                    'expected': f"{expected['retailer']} / {expected['processor']}"
                })
        else:
            # Store in HTML but not in Excel tabs
            extra_in_html.append({
                'sn': sn,
                'retailer': current_retailer,
                'processor': current_processor,
                'location': f"{store['city']}, {store['state']}"
            })
    
    # Check for stores in Excel but not in HTML
    html_store_numbers = set(str(s['sn']) for s in stores)
    for sn, expected in expected_assignments.items():
        if sn not in html_store_numbers:
            missing_from_html.append({
                'sn': sn,
                'expected': f"{expected['retailer']} / {expected['processor']}"
            })
    
    # Print results
    print(f'\n{"="*80}')
    print('AUDIT RESULTS')
    print(f'{"="*80}')
    
    if mismatches:
        print(f'\n❌ MISMATCHES FOUND: {len(mismatches)}')
        print('-' * 80)
        for m in mismatches[:20]:  # Show first 20
            print(f"Store #{m['sn']}: Current={m['current']} | Expected={m['expected']}")
        if len(mismatches) > 20:
            print(f'... and {len(mismatches) - 20} more mismatches')
    else:
        print('\n✓ No mismatches found - all stores match Excel source')
    
    if missing_from_html:
        print(f'\n❌ MISSING FROM HTML: {len(missing_from_html)} stores')
        print('-' * 80)
        for m in missing_from_html[:10]:
            print(f"Store #{m['sn']}: Expected {m['expected']}")
        if len(missing_from_html) > 10:
            print(f'... and {len(missing_from_html) - 10} more missing stores')
    else:
        print('\n✓ No missing stores - all Excel stores are in HTML')
    
    if extra_in_html:
        print(f'\n⚠️  EXTRA IN HTML: {len(extra_in_html)} stores not in Excel tabs')
        print('-' * 80)
        for e in extra_in_html[:10]:
            print(f"Store #{e['sn']}: {e['retailer']} / {e['processor']} - {e['location']}")
        if len(extra_in_html) > 10:
            print(f'... and {len(extra_in_html) - 10} more extra stores')
    else:
        print('\n✓ No extra stores - all HTML stores are in Excel')
    
    # Summary by retailer/processor
    print(f'\n{"="*80}')
    print('CURRENT HTML DISTRIBUTION')
    print(f'{"="*80}')
    
    retailer_proc_counts = {}
    for store in stores:
        key = f"{store['retailer']} / {store['processor']}"
        retailer_proc_counts[key] = retailer_proc_counts.get(key, 0) + 1
    
    for combo in sorted(retailer_proc_counts.keys()):
        print(f'{combo}: {retailer_proc_counts[combo]} stores')
    
    # Save detailed results
    audit_results = {
        'mismatches': mismatches,
        'missing_from_html': missing_from_html,
        'extra_in_html': extra_in_html
    }
    
    with open('audit_results.json', 'w') as f:
        json.dump(audit_results, f, indent=2)
    
    print(f'\n✓ Detailed audit results saved to audit_results.json')
