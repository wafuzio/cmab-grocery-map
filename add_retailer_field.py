import json
import re

# Read the HTML file
with open('/Users/dan.maguire/Downloads/WMT Stores/WMT Store Map.html', 'r') as f:
    html_content = f.read()

# Extract the STORES array
match = re.search(r'const STORES = (\[.*?\]);', html_content, re.DOTALL)
stores = json.loads(match.group(1))

print(f"Adding 'retailer' field to {len(stores)} stores...")

# Add retailer field (currently all Walmart)
# Also rename 'ret' to 'processor' for clarity
for store in stores:
    store['retailer'] = 'Walmart'
    store['processor'] = store.pop('ret')  # Rename ret to processor

print(f"✓ Added retailer field and renamed 'ret' to 'processor'")

# Write back to HTML
new_stores_json = json.dumps(stores, separators=(',', ': '))
new_html = html_content.replace(match.group(1), new_stores_json)

with open('/Users/dan.maguire/Downloads/WMT Stores/WMT Store Map.html', 'w') as f:
    f.write(new_html)

print(f"✓ Updated HTML file")
