import json
import requests
import time

# Read delivery zip codes
with open('/Users/dan.maguire/Downloads/WMT Stores/gopuff_delivery_data.json', 'r') as f:
    delivery_zips = json.load(f)

print(f'Total delivery zip codes: {len(delivery_zips)}')

# We'll use a public API to get zip code boundaries
# Option 1: Use OpenDataSoft's US ZIP Code Database API
# Option 2: Download a complete US zip code GeoJSON file

# For this implementation, we'll create a solution that loads zip boundaries dynamically
# using a CDN-hosted zip code boundary dataset

# Create a list of all zip codes we need
zip_codes = [d['zip'] for d in delivery_zips]

print(f'\nZip codes to display: {len(zip_codes)}')
print(f'Sample zips: {zip_codes[:10]}')

# Save the zip code list for the map to use
with open('/Users/dan.maguire/Downloads/WMT Stores/delivery_zip_list.json', 'w') as f:
    json.dump(zip_codes, f)

print('\n✓ Saved delivery zip code list to delivery_zip_list.json')

# Create a simplified approach: use a public zip code boundary service
# We'll modify the HTML to load zip boundaries from a CDN or API
print('\nNote: Will use public zip code boundary data in the map implementation')
