import json
import re

with open('Processor_Map.html', 'r', encoding='utf-8') as f:
    content = f.read()

match = re.search(r'const STORES = (\[.*?\]);', content, re.DOTALL)
if match:
    stores = json.loads(match.group(1))
    
    # Find store #1825
    store_1825 = next((s for s in stores if s['sn'] == '1825'), None)
    if store_1825:
        print('Store #1825 details:')
        for key, val in store_1825.items():
            print(f'  {key}: {val}')
    
    # Check how many stores are currently labeled as each retailer
    print('\nCurrent retailer distribution:')
    retailers = {}
    for s in stores:
        ret = s['retailer']
        retailers[ret] = retailers.get(ret, 0) + 1
    
    for ret in sorted(retailers.keys()):
        print(f'  {ret}: {retailers[ret]} stores')
    
    # Check all Safeway stores to see their processors
    safeway_stores = [s for s in stores if s['retailer'] == 'Safeway']
    print(f'\nSafeway stores by processor:')
    processors = {}
    for s in safeway_stores:
        proc = s['processor']
        processors[proc] = processors.get(proc, 0) + 1
    
    for proc in sorted(processors.keys()):
        print(f'  {proc}: {processors[proc]} stores')
    
    # Show some examples of Safeway stores with non-Crystal Creamery processors
    print('\nSafeway stores with non-Crystal Creamery processors:')
    non_cc = [s for s in safeway_stores if s['processor'] != 'Crystal Creamery']
    for s in non_cc[:10]:
        print(f"  Store #{s['sn']}: {s['city']}, {s['state']} - Processor: {s['processor']}")
