import re

# Read the HTML file
with open('/Users/dan.maguire/Downloads/WMT Stores/WMT Store Map.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# Read the Lucerne logo data URI
with open('/Users/dan.maguire/Downloads/WMT Stores/lucerne_logo_uri.txt', 'r') as f:
    lucerne_logo = f.read().strip()

print(f"Lucerne logo length: {len(lucerne_logo)} characters")

# Find and replace the Lucerne placeholder in RETAILER_LOGOS
# Look for the existing Lucerne entry (which has a placeholder SVG)
pattern = r"'Lucerne': 'data:image/svg+xml[^']+'"
match = re.search(pattern, html_content)

if match:
    old_lucerne = match.group(0)
    new_lucerne = f"'Lucerne': '{lucerne_logo}'"
    html_content = html_content.replace(old_lucerne, new_lucerne)
    print('✓ Replaced existing Lucerne placeholder with actual PNG logo')
else:
    print('✗ Could not find Lucerne placeholder')
    # Try to add it after Crystal Creamery
    pattern = r"('Crystal Creamery': 'data:image[^']+'),\s*('Hollandia')"
    match = re.search(pattern, html_content)
    if match:
        html_content = html_content.replace(match.group(0), f"{match.group(1)},\n  'Lucerne': '{lucerne_logo}',\n  {match.group(2)}")
        print('✓ Added Lucerne logo after Crystal Creamery')

# Write back
with open('/Users/dan.maguire/Downloads/WMT Stores/WMT Store Map.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print('✓ Lucerne logo successfully updated in map')
