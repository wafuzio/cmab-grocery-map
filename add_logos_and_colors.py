import re
import base64

# Read the base64 data
with open('safeway_logo_base64.txt', 'r') as f:
    safeway_b64 = f.read()

with open('vons_logo_base64.txt', 'r') as f:
    vons_b64 = f.read()

# Read the HTML file
with open('Processor_Map.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and update RETAILER_COLORS
match = re.search(r"const RETAILER_COLORS = \{[^}]+\};", content, re.DOTALL)
if match:
    old_colors = match.group(0)
    # Add Safeway and Vons with their red color
    new_colors = old_colors.replace("};", ", 'Safeway': '#E31837', 'Vons': '#E31837'};")
    content = content.replace(old_colors, new_colors)
    print('✓ Added Safeway and Vons to RETAILER_COLORS')

# Find and update RETAILER_BADGE_COLORS
match = re.search(r"const RETAILER_BADGE_COLORS = \{[^}]+\};", content, re.DOTALL)
if match:
    old_badge_colors = match.group(0)
    new_badge_colors = old_badge_colors.replace("};", ", 'Safeway': '#E31837', 'Vons': '#E31837'};")
    content = content.replace(old_badge_colors, new_badge_colors)
    print('✓ Added Safeway and Vons to RETAILER_BADGE_COLORS')

# Find RETAILER_LOGOS - this is more complex due to the large base64 data
# We need to find the line and add our logos
match = re.search(r'const RETAILER_LOGOS = \{[^;]+\};', content, re.DOTALL)
if match:
    old_logos = match.group(0)
    # Add Safeway and Vons logos before the closing brace
    safeway_entry = f'"Safeway": "data:image/png;base64,{safeway_b64}"'
    vons_entry = f'"Vons": "data:image/png;base64,{vons_b64}"'
    
    new_logos = old_logos.replace('};', f', {safeway_entry}, {vons_entry}}};')
    content = content.replace(old_logos, new_logos)
    print('✓ Added Safeway and Vons logos to RETAILER_LOGOS')

# Write back
with open('Processor_Map.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('\n✓ Successfully updated Processor_Map.html with Safeway and Vons logos and colors')
