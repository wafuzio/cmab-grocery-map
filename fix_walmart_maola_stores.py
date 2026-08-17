import json
import re

# Read the HTML file
with open('Processor_Map.html', 'r', encoding='utf-8') as f:
    content = f.read()

match = re.search(r'const STORES = (\[.*?\]);', content, re.DOTALL)
if match:
    stores = json.loads(match.group(1))
    
    print(f'Total stores: {len(stores)}')
    
    # Find stores that have Maola or Sarah Farms processor but are labeled as Safeway/Vons/Albertsons
    # These should be Walmart stores
    fixed_count = 0
    
    for store in stores:
        processor = store['processor']
        retailer = store['retailer']
        
        # Maola and Sarah Farms only serve Walmart stores
        if processor in ['Maola', 'Sarah Farms']:
            if retailer != 'Walmart':
                print(f'Fixing Store #{store["sn"]}: {retailer} → Walmart (Processor: {processor})')
                store['retailer'] = 'Walmart'
                fixed_count += 1
    
    print(f'\nFixed {fixed_count} stores that should be Walmart')
    
    # Show final distribution
    retailer_counts = {}
    for store in stores:
        ret = store['retailer']
        retailer_counts[ret] = retailer_counts.get(ret, 0) + 1
    
    print('\nFinal retailer distribution:')
    for retailer in sorted(retailer_counts.keys()):
        print(f'  {retailer}: {retailer_counts[retailer]} stores')
    
    # Verify store #1825
    store_1825 = next((s for s in stores if s['sn'] == '1825'), None)
    if store_1825:
        print(f'\nStore #1825:')
        print(f'  Retailer: {store_1825["retailer"]}')
        print(f'  Processor: {store_1825["processor"]}')
    
    # Convert back to JSON
    new_stores_json = json.dumps(stores, separators=(',', ':'))
    
    # Replace in content
    new_content = content.replace(match.group(0), f'const STORES = {new_stores_json};')
    
    # Write back
    with open('Processor_Map.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print('\n✓ Fixed Walmart stores that were incorrectly labeled')
