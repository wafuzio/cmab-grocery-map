"""Build a combined California grocery map data file.

Merges:
  1. Existing MilkPEP/TDA stores from processor_map_data.json (CA only)
  2. Audited SNAP-authorized grocery destinations from ca_grocery_stores_audited.csv

The audited CSV includes normalized banner names, banner groups, and
suggested store types (e.g. "Hispanic Grocer", "Hispanic Meat Market")
from the Devin AI audit pass.

Deduplication: if a SNAP store's normalized address matches an existing
MilkPEP/TDA store, the records are merged (SNAP source flag added) rather
than duplicated.

Output: data/ca_grocer_map_data.json
"""
import csv
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
EXISTING_PATH = DATA_DIR / "processor_map_data.json"
AUDITED_CSV_PATH = DATA_DIR / "ca_grocery_stores_audited.csv"
OUTPUT_PATH = DATA_DIR / "ca_grocer_map_data.json"


def normalize_addr(addr: str, city: str) -> str:
    """Build a stable address key for dedup matching."""
    parts = [
        re.sub(r"[^a-z0-9]", "", (addr or "").lower()),
        re.sub(r"[^a-z0-9]", "", (city or "").lower()),
    ]
    return "|".join(p for p in parts if p)


def main() -> None:
    # --- Load existing MilkPEP/TDA stores, filter to CA ---
    with EXISTING_PATH.open() as f:
        existing = json.load(f)

    ca_stores = [s for s in existing["stores"] if s.get("state") == "CA"]

    # Add store_type for existing stores so the filter dimension is uniform
    for s in ca_stores:
        s["store_type"] = "MilkPEP/TDA"

    # Build address index for dedup
    addr_index: dict[str, int] = {}
    for i, s in enumerate(ca_stores):
        key = normalize_addr(s.get("addr", ""), s.get("city", ""))
        if key:
            addr_index[key] = i

    # --- Load audited SNAP grocers ---
    snap_stores = []
    with AUDITED_CSV_PATH.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            lat = float(row["Lat"]) if row.get("Lat") else None
            lon = float(row["Lon"]) if row.get("Lon") else None
            if lat is None or lon is None:
                continue

            # Use Suggested_Store_Type if available, fall back to Store Type
            store_type = (row.get("Suggested_Store_Type") or row.get("Store Type", "")).strip()
            # Use Normalized_Banner_Group if available
            banner_group = (row.get("Normalized_Banner_Group") or "Misc.").strip()
            banner = (row.get("Normalized_Banner") or row.get("Banner", "")).strip()
            addr = row.get("Address", "").strip()
            city = row.get("City", "").strip()

            record = {
                "id": f"SNAP|{row['Store #']}",
                "sn": row.get("Store #", ""),
                "banner": banner,
                "holding_co": row.get("Holding Co.", "").strip(),
                "processor": row.get("Processor", "").strip(),
                "owner": row.get("Holding Co.", "").strip(),
                "addr": addr,
                "city": city,
                "state": "CA",
                "zip": row.get("Zip", "").strip(),
                "lat": lat,
                "lon": lon,
                "region": "West",
                "store_type": store_type,
                "banner_group": banner_group,
                "county": row.get("County", "").strip(),
            }

            # Check for address match with existing MilkPEP/TDA store
            addr_key = normalize_addr(addr, city)
            if addr_key and addr_key in addr_index:
                idx = addr_index[addr_key]
                existing_rec = ca_stores[idx]
                # Mark as also in SNAP, keep existing record
                existing_rec["store_type"] = "MilkPEP/TDA + SNAP"
                # Don't add the SNAP record — it's a dup
                continue

            snap_stores.append(record)

    all_stores = ca_stores + snap_stores

    all_stores.sort(key=lambda s: (s.get("city", ""), s.get("banner", "")))

    # --- Build summary ---
    store_type_counts = Counter(s.get("store_type", "") for s in all_stores)
    banner_group_counts = Counter(s.get("banner_group", "") for s in all_stores)
    major_banners = {name for name, count in banner_group_counts.items() if count >= 3 and name != "Misc."}

    summary = {
        "store_count_total": len(all_stores),
        "store_count_milkpep_tda": len(ca_stores),
        "store_count_snap_new": len(snap_stores),
        "store_type_counts": dict(sorted(store_type_counts.items())),
        "banner_group_counts": dict(sorted(banner_group_counts.items())),
        "major_banners": sorted(major_banners),
        "states": {"CA": len(all_stores)},
    }

    output = {
        "stores": all_stores,
        "meta": {
            "summary": summary,
        },
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2))
    print(f"CA MilkPEP/TDA stores: {len(ca_stores)}")
    print(f"New SNAP stores: {len(snap_stores)}")
    print(f"Total: {len(all_stores)}")
    print()
    print("Store type counts:")
    print(json.dumps(dict(sorted(store_type_counts.items())), indent=2))
    print()
    print(f"Written to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
