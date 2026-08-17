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
    
    print(f'Total stores in dataset: {len(stores)}')
    print()
    
    # Count Albertsons stores
    albertsons_stores = [s for s in stores if s['retailer'] == 'Albertsons']
    print(f'Albertsons stores: {len(albertsons_stores)}')
    
    # Count Lucerne processors
    lucerne_stores = [s for s in stores if s['processor'] == 'Lucerne']
    print(f'Lucerne processor stores: {len(lucerne_stores)}')
    print()
    
    # Find Albertsons stores that are NOT Lucerne
    albertsons_not_lucerne = [s for s in albertsons_stores if s['processor'] != 'Lucerne']
    
    print(f'Albertsons stores WITHOUT Lucerne processor: {len(albertsons_not_lucerne)}')
    print()
    
    if albertsons_not_lucerne:
        # Group by processor
        by_processor = {}
        for store in albertsons_not_lucerne:
            proc = store['processor']
            if proc not in by_processor:
                by_processor[proc] = []
            by_processor[proc].append(store)
        
        print('Breakdown by processor:')
        for proc in sorted(by_processor.keys()):
            print(f'  {proc}: {len(by_processor[proc])} stores')
        print()
        
        # Show first 20 examples
        print('First 20 Albertsons stores with non-Lucerne processors:')
        for i, store in enumerate(albertsons_not_lucerne[:20], 1):
            print(f'  {i}. Store #{store["sn"]} - {store["city"]}, {store["state"]} - Processor: {store["processor"]}')
        
        if len(albertsons_not_lucerne) > 20:
            print(f'  ... and {len(albertsons_not_lucerne) - 20} more')
    
    # Also check: are there any Lucerne stores that are NOT Albertsons?
    print()
    lucerne_not_albertsons = [s for s in lucerne_stores if s['retailer'] != 'Albertsons']
    print(f'Lucerne processor stores WITHOUT Albertsons retailer: {len(lucerne_not_albertsons)}')
    
    if lucerne_not_albertsons:
        # Group by retailer
        by_retailer = {}
        for store in lucerne_not_albertsons:
            ret = store['retailer']
            if ret not in by_retailer:
                by_retailer[ret] = []
            by_retailer[ret].append(store)
        
        print('Breakdown by retailer:')
        for ret in sorted(by_retailer.keys()):
            print(f'  {ret}: {len(by_retailer[ret])} stores')
        print()
        
        # Show first 10 examples
        print('First 10 Lucerne stores with non-Albertsons retailers:')
        for i, store in enumerate(lucerne_not_albertsons[:10], 1):
            print(f'  {i}. Store #{store["sn"]} - {store["retailer"]} - {store["city"]}, {store["state"]}')
        
        if len(lucerne_not_albertsons) > 10:
            print(f'  ... and {len(lucerne_not_albertsons) - 10} more')
    
else:
    print('ERROR: Could not find STORES array in HTML file')
