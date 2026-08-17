"""Extract California grocery destinations from the SNAP retailer data.

Includes every store type that could be a household's primary milk-buying
destination: Grocery Store, Supermarket, Super Store, plus Convenience
Store and Other entries that look like neighborhood markets.

Excludes liquor stores, pharmacies, and dollar stores by name pattern.

The Store_Type column is preserved so consumers can easily include or
exclude convenience stores after the fact.
"""
import re
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).parent
INPUT = ROOT / "final store lists" / "CA_SNAP_Retailer_Location_data.xlsx"
OUTPUT = ROOT / "data" / "ca_snap_grocers.csv"

# Store types that are always included.
ALWAYS_INCLUDE_TYPES = {"Grocery Store", "Supermarket", "Super Store"}

# Store types where we filter by name to keep neighborhood markets.
FILTERED_TYPES = {"Convenience Store", "Other"}

# Name patterns that suggest a neighborhood market / grocery destination.
MARKET_KEYWORDS = re.compile(
    r"MARKET|MERCADO|FOOD|GROCERY|MART|SUPERMERCADO|CARNICERIA|PRODUCE|MINI\s*MART",
    re.IGNORECASE,
)

# Name patterns that indicate liquor, pharmacy, or dollar stores — excluded.
EXCLUDE_KEYWORDS = re.compile(
    r"LIQUOR|SPIRITS|WINE|BEER|ALCOHOL|"
    r"WALGREENS|RITE AID|CVS|PHARMACY|DRUG|"
    r"DOLLAR\s*(TREE|GENERAL|STORE)|DOLLAR\s",
    re.IGNORECASE,
)

# Gas station / fast-stop chains — excluded even if name has "market".
GAS_KEYWORDS = re.compile(
    r"7-ELEVEN|7\sELEVEN|CIRCLE\sK|QUIK\sSTOP|SHELL|CHEVRON|MOBIL|"
    r"VALERO|ARCO|FASTRIP|FAST\s*STOP|FASTRACK|SINCLAIR|"
    r"AM/PM|AMPM|BP\s|EXXON|TEXACO|UNION\s76|76\s",
    re.IGNORECASE,
)


def should_include(row: pd.Series) -> bool:
    store_type = str(row.get("Store_Type", "")).strip()
    name = str(row.get("Store_Name", "")).strip()

    if store_type in ALWAYS_INCLUDE_TYPES:
        return True

    if store_type not in FILTERED_TYPES:
        return False

    # Exclude liquor, pharmacy, dollar regardless of market keyword.
    if EXCLUDE_KEYWORDS.search(name):
        return False

    # Exclude gas stations even if they say "market".
    if GAS_KEYWORDS.search(name):
        return False

    # Keep if the name has a market-like keyword.
    if MARKET_KEYWORDS.search(name):
        return True

    return False


def main() -> None:
    df = pd.read_excel(INPUT, dtype=str)
    df.columns = [c.strip() for c in df.columns]

    df["include"] = df.apply(should_include, axis=1)
    result = df[df["include"]].drop(columns=["include"])

    # Select and rename columns for clean output.
    result = result[[
        "Record_ID", "Store_Name", "Store_Type",
        "Store_Street_Address", "City", "State", "Zip_Code", "Zip4",
        "County", "Latitude", "Longitude",
    ]].copy()
    result.columns = [
        "record_id", "store_name", "store_type",
        "address", "city", "state", "zip", "zip4",
        "county", "lat", "lon",
    ]

    result = result.sort_values(["store_type", "county", "city", "store_name"])

    OUTPUT.parent.mkdir(exist_ok=True)
    result.to_csv(OUTPUT, index=False)

    print(f"Total rows in source: {len(df)}")
    print(f"Extracted: {len(result)}")
    print()
    print("Breakdown by store_type:")
    print(result["store_type"].value_counts().to_string())
    print()
    print(f"Written to {OUTPUT}")


if __name__ == "__main__":
    main()
