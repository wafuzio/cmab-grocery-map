import re

# Read the Lucerne logo data URI
with open('/Users/dan.maguire/Downloads/WMT Stores/lucerne_logo_uri.txt', 'r') as f:
    lucerne_logo = f.read().strip()

print(f"Lucerne logo size: {len(lucerne_logo)} characters")

# Read the HTML file
with open('/Users/dan.maguire/Downloads/WMT Stores/WMT Store Map.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# Find the line with RETAILER_LOGOS
# We need to insert Lucerne into the JSON object
# Look for the pattern and insert after Hollandia or Maola

# Find the RETAILER_LOGOS line (it's all on one line)
pattern = r'(const RETAILER_LOGOS = \{[^}]+)(\})'
match = re.search(pattern, html_content)

if match:
    logos_part = match.group(1)
    closing_brace = match.group(2)
    
    # Check if Lucerne already exists
    if '"Lucerne"' in logos_part or "'Lucerne'" in logos_part:
        print("Lucerne already exists in RETAILER_LOGOS")
    else:
        # Add Lucerne before the closing brace
        new_logos = f'{logos_part}, "Lucerne": "{lucerne_logo}"{closing_brace}'
        html_content = html_content.replace(match.group(0), new_logos)
        print("✓ Added Lucerne logo to RETAILER_LOGOS")
        
        # Write back
        with open('/Users/dan.maguire/Downloads/WMT Stores/WMT Store Map.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        print("✓ File saved successfully")
else:
    print("✗ Could not find RETAILER_LOGOS pattern")
