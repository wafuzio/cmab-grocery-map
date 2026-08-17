import pandas as pd
import json
import re

# Read the promo Excel file to get store numbers by banner
xl = pd.ExcelFile('2026 MilkPEP Neptune Supergirl Promo.xlsx')

# Crystal Creamery - Safeway stores
df_cc_safeway = pd.read_excel('2026 MilkPEP Neptune Supergirl Promo.xlsx', sheet_name='Crystal Creamery - Safeway', header=1)
print('Crystal Creamery - Safeway tab columns:', df_cc_safeway.columns.tolist())
print('First few rows:')
print(df_cc_safeway.head(10))

# Try to find store numbers - look in 'Name' column for store numbers
safeway_stores = []
if 'Name' in df_cc_safeway.columns:
    for name in df_cc_safeway['Name'].dropna():
        # Extract store number from name like "Safeway #1234" or just numbers
        match = re.search(r'#?(\d{3,4})', str(name))
        if match:
            safeway_stores.append(int(match.group(1)))

print(f'\nFound {len(safeway_stores)} Safeway stores')
print('Sample store numbers:', safeway_stores[:10] if safeway_stores else 'None')

print('\n' + '='*60)

# Hollandia - Albertsons stores
df_holl_alb = pd.read_excel('2026 MilkPEP Neptune Supergirl Promo.xlsx', sheet_name='Hollandia - Albertsons', header=1)
print('\nHollandia - Albertsons tab columns:', df_holl_alb.columns.tolist())
print('First few rows:')
print(df_holl_alb.head(10))

# Extract store numbers from "Albertsons #XXXX" format
albertsons_stores = []
for col in df_holl_alb.columns:
    for val in df_holl_alb[col].dropna():
        val_str = str(val)
        if 'Albertsons #' in val_str or 'Vons #' in val_str:
            # Extract number after #
            match = re.search(r'#(\d+)', val_str)
            if match:
                albertsons_stores.append(int(match.group(1)))

print(f'\nFound {len(albertsons_stores)} Albertsons/Vons stores from Hollandia tab')
print('Sample store numbers:', albertsons_stores[:10] if albertsons_stores else 'None')
