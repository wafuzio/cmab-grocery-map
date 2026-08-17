import json
import re

# Load the geocoded Albertsons stores
with open('/Users/dan.maguire/Downloads/WMT Stores/albertsons_geocoded.json', 'r') as f:
    albertsons_stores = json.load(f)

print(f"Loading {len(albertsons_stores)} Albertsons stores...")

# Read the HTML file
with open('/Users/dan.maguire/Downloads/WMT Stores/WMT Store Map.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# Find the STORES array
stores_match = re.search(r'const STORES = (\[.*?\]);', html_content, re.DOTALL)
if not stores_match:
    print("ERROR: Could not find STORES array")
    exit(1)

stores_json = stores_match.group(1)
walmart_stores = json.loads(stores_json)

print(f"Found {len(walmart_stores)} existing Walmart stores")

# Add Lucerne to processor logos and colors
# Check if Lucerne is already in the logos
if 'Lucerne' not in html_content:
    print("Adding Lucerne processor to logos and colors...")
    
    # Add Lucerne logo
    logo_section = re.search(r"(const RETAILER_LOGOS = \{[^}]+)'Sarah Farms': 'data:image[^']+'\s*\};", html_content, re.DOTALL)
    if logo_section:
        # Add Lucerne logo (using a placeholder - will need actual logo)
        lucerne_logo = "'Lucerne': 'data:image/svg+xml,%3Csvg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 100 100\"%3E%3Ccircle cx=\"50\" cy=\"50\" r=\"45\" fill=\"%23D32F2F\"/%3E%3Ctext x=\"50\" y=\"60\" text-anchor=\"middle\" fill=\"white\" font-size=\"24\" font-weight=\"bold\"%3EL%3C/text%3E%3C/svg%3E'"
        
        html_content = html_content.replace(
            "'Sarah Farms': 'data:image",
            f"{lucerne_logo},\n  'Sarah Farms': 'data:image"
        )
    
    # Add Lucerne color
    color_section = re.search(r"(const PROCESSOR_COLORS = \{[^}]+)'Sarah Farms': '#6A1B9A'\s*\};", html_content, re.DOTALL)
    if color_section:
        html_content = html_content.replace(
            "'Sarah Farms': '#6A1B9A'",
            "'Lucerne': '#D32F2F',\n  'Sarah Farms': '#6A1B9A'"
        )

# Combine all stores
all_stores = walmart_stores + albertsons_stores

print(f"Total stores: {len(all_stores)}")
print(f"  Walmart: {len(walmart_stores)}")
print(f"  Albertsons: {len(albertsons_stores)}")

# Count by processor
processors = {}
for store in all_stores:
    proc = store['processor']
    processors[proc] = processors.get(proc, 0) + 1

print("\nStores by processor:")
for proc, count in sorted(processors.items()):
    print(f"  {proc}: {count}")

# Replace the STORES array in the HTML
new_stores_json = json.dumps(all_stores, indent=0, separators=(',', ':')).replace('\n', '')
html_content = html_content.replace(stores_json, new_stores_json)

# Write back to HTML file
with open('/Users/dan.maguire/Downloads/WMT Stores/WMT Store Map.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"\n✓ Successfully updated map with {len(all_stores)} total stores")
print("✓ Albertsons stores will display with green borders")
print("✓ Lucerne processor added to the map")
