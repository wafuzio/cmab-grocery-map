import json
import re

# Read the HTML file
with open('Processor_Map.html', 'r', encoding='utf-8') as f:
    content = f.read()

match = re.search(r'const STORES = (\[.*?\]);', content, re.DOTALL)
if match:
    stores = json.loads(match.group(1))
    
    print(f'Total stores before fix: {len(stores)}')
    
    # Find the 2 Vons stores
    vons_stores = [s for s in stores if s['retailer'] == 'Vons']
    print(f'\nCurrent Vons stores: {len(vons_stores)}')
    for s in vons_stores:
        print(f'  Store #{s["sn"]}: {s["city"]}, {s["state"]} - Processor: {s["processor"]}')
    
    # According to the Hollandia - Albertsons tab, these 2 Vons stores should have Hollandia processor
    # Store #2142 and #2344
    
    # Update the processor for these stores
    fixed_count = 0
    for store in stores:
        if store['retailer'] == 'Vons' and store['sn'] in ['2142', '2344']:
            if store['processor'] != 'Hollandia':
                print(f'\nFixing Store #{store["sn"]}: {store["processor"]} → Hollandia')
                store['processor'] = 'Hollandia'
                fixed_count += 1
    
    print(f'\nFixed {fixed_count} Vons stores to use Hollandia processor')
    
    # Verify final state
    vons_final = [s for s in stores if s['retailer'] == 'Vons']
    print(f'\nFinal Vons stores: {len(vons_final)}')
    for s in vons_final:
        print(f'  Store #{s["sn"]}: {s["city"]}, {s["state"]} - Processor: {s["processor"]}')
    
    # Show processor distribution for Vons
    print('\nVons stores by processor:')
    proc_counts = {}
    for s in vons_final:
        proc = s['processor']
        proc_counts[proc] = proc_counts.get(proc, 0) + 1
    for proc, count in sorted(proc_counts.items()):
        print(f'  {proc}: {count}')
    
    # Convert back to JSON
    new_stores_json = json.dumps(stores, separators=(',', ':'))
    
    # Replace in content
    new_content = content.replace(match.group(0), f'const STORES = {new_stores_json};')
    
    # Write back
    with open('Processor_Map.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print('\n✓ Corrected Vons stores to use Hollandia processor per Excel source')
