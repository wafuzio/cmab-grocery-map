import json
import re

# Read the HTML file
with open('/Users/dan.maguire/Downloads/WMT Stores/Processor_Map.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract STORES array
match = re.search(r'const STORES = (\[.*?\]);', content, re.DOTALL)
if match:
    stores_json = match.group(1)
    stores = json.loads(stores_json)
    
    # Check what fields are available in a store object
    if stores:
        print('Available fields in store objects:')
        sample_store = stores[0]
        for key in sorted(sample_store.keys()):
            print(f'  {key}: {sample_store[key]}')
        
        print('\n' + '='*60)
        print('Sample Crystal Creamery store:')
        crystal_store = next((s for s in stores if s['processor'] == 'Crystal Creamery'), None)
        if crystal_store:
            for key in sorted(crystal_store.keys()):
                print(f'  {key}: {crystal_store[key]}')
        
        print('\n' + '='*60)
        print('Sample Hollandia store:')
        hollandia_store = next((s for s in stores if s['processor'] == 'Hollandia'), None)
        if hollandia_store:
            for key in sorted(hollandia_store.keys()):
                print(f'  {key}: {hollandia_store[key]}')
else:
    print('ERROR: Could not find STORES array in HTML file')
