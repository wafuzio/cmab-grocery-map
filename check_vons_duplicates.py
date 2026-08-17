import json
import re

# Read the HTML file
with open('Processor_Map.html', 'r', encoding='utf-8') as f:
    content = f.read()

match = re.search(r'const STORES = (\[.*?\]);', content, re.DOTALL)
if match:
    stores = json.loads(match.group(1))
    
    # Find all Vons stores
    vons_stores = [s for s in stores if s['retailer'] == 'Vons']
    
    print(f'Total Vons store entries: {len(vons_stores)}')
    print('\nDuplicate stores found:')
    
    # Group by store number
    by_sn = {}
    for s in vons_stores:
        sn = s['sn']
        if sn not in by_sn:
            by_sn[sn] = []
        by_sn[sn].append(s)
    
    # Show duplicates
    for sn, store_list in by_sn.items():
        if len(store_list) > 1:
            print(f'\nStore #{sn} ({store_list[0]["city"]}, {store_list[0]["state"]}) - {len(store_list)} entries:')
            for s in store_list:
                print(f'  Processor: {s["processor"]}')
    
    # Remove Hollandia duplicates, keep Lucerne
    print('\n' + '='*60)
    print('Removing Hollandia duplicates, keeping Lucerne entries...')
    
    # Create a set of (sn, processor) tuples we've seen
    seen = set()
    stores_to_keep = []
    removed_count = 0
    
    for store in stores:
        key = (store['sn'], store['retailer'])
        
        # For Vons stores, prefer Lucerne over Hollandia
        if store['retailer'] == 'Vons':
            # Check if we've seen this store number before
            sn = store['sn']
            existing_vons = [s for s in stores_to_keep if s['sn'] == sn and s['retailer'] == 'Vons']
            
            if existing_vons:
                # We already have this Vons store
                existing_proc = existing_vons[0]['processor']
                current_proc = store['processor']
                
                # Keep Lucerne, remove Hollandia
                if current_proc == 'Lucerne' and existing_proc == 'Hollandia':
                    # Replace the Hollandia entry with Lucerne
                    stores_to_keep.remove(existing_vons[0])
                    stores_to_keep.append(store)
                    removed_count += 1
                    print(f'  Replaced Store #{sn} Hollandia with Lucerne')
                elif current_proc == 'Hollandia' and existing_proc == 'Lucerne':
                    # Skip this Hollandia entry, keep existing Lucerne
                    removed_count += 1
                    print(f'  Skipped Store #{sn} Hollandia duplicate')
                    continue
                else:
                    # Both same processor or different non-Hollandia/Lucerne
                    stores_to_keep.append(store)
            else:
                # First time seeing this Vons store
                stores_to_keep.append(store)
        else:
            # Not a Vons store, keep as is
            stores_to_keep.append(store)
    
    print(f'\nRemoved {removed_count} duplicate entries')
    print(f'Total stores after deduplication: {len(stores_to_keep)}')
    
    # Verify Vons stores
    vons_final = [s for s in stores_to_keep if s['retailer'] == 'Vons']
    print(f'\nFinal Vons stores: {len(vons_final)}')
    for s in vons_final:
        print(f'  Store #{s["sn"]}: {s["city"]}, {s["state"]} - Processor: {s["processor"]}')
    
    # Convert back to JSON
    new_stores_json = json.dumps(stores_to_keep, separators=(',', ':'))
    
    # Replace in content
    new_content = content.replace(match.group(0), f'const STORES = {new_stores_json};')
    
    # Write back
    with open('Processor_Map.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print('\n✓ Removed duplicate Vons stores')
