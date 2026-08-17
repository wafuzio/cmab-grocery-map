import json
import re

# Load expected assignments from Excel
with open('expected_assignments.json', 'r') as f:
    expected_assignments = json.load(f)

print(f'Loaded {len(expected_assignments)} expected store assignments from Excel')

# Read the HTML file
with open('Processor_Map.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract STORES array
match = re.search(r'const STORES = (\[.*?\]);', content, re.DOTALL)
if match:
    stores = json.loads(match.group(1))
    
    print(f'Current stores in HTML: {len(stores)}')
    
    # Update stores that are in the Excel mapping
    updated_count = 0
    stores_in_excel = set(expected_assignments.keys())
    html_store_numbers = set(str(s['sn']) for s in stores)
    
    # Update existing stores
    for store in stores:
        sn = str(store['sn'])
        if sn in expected_assignments:
            expected = expected_assignments[sn]
            if store['retailer'] != expected['retailer'] or store['processor'] != expected['processor']:
                old = f"{store['retailer']}/{store['processor']}"
                store['retailer'] = expected['retailer']
                store['processor'] = expected['processor']
                new = f"{store['retailer']}/{store['processor']}"
                updated_count += 1
                if updated_count <= 10:
                    print(f'  Updated Store #{sn}: {old} → {new}')
    
    print(f'\nUpdated {updated_count} stores to match Excel source')
    
    # Check for stores in Excel but not in HTML
    missing_stores = stores_in_excel - html_store_numbers
    print(f'\nStores in Excel but not in HTML: {len(missing_stores)}')
    if missing_stores:
        print(f'  Sample missing store numbers: {sorted(list(missing_stores))[:10]}')
    
    # Check for stores in HTML but not in Excel
    extra_stores = html_store_numbers - stores_in_excel
    print(f'\nStores in HTML but not in Excel: {len(extra_stores)}')
    if extra_stores:
        print(f'  Sample extra store numbers: {sorted(list(extra_stores))[:10]}')
    
    # Show final distribution
    print(f'\n{"="*80}')
    print('FINAL STORE DISTRIBUTION AFTER UPDATE')
    print(f'{"="*80}')
    
    retailer_counts = {}
    for store in stores:
        ret = store['retailer']
        retailer_counts[ret] = retailer_counts.get(ret, 0) + 1
    
    for retailer in sorted(retailer_counts.keys()):
        print(f'{retailer}: {retailer_counts[retailer]} stores')
    
    print(f'\nTotal stores: {len(stores)}')
    
    # Convert back to JSON
    new_stores_json = json.dumps(stores, separators=(',', ':'))
    
    # Replace in content
    new_content = content.replace(match.group(0), f'const STORES = {new_stores_json};')
    
    # Write back
    with open('Processor_Map.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print('\n✓ Updated all stores to match Excel source')
else:
    print('ERROR: Could not find STORES array in HTML file')
