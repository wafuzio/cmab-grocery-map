#!/usr/bin/env python3
"""Sync ca_grocer_map_data.json banner_group/banner/web_url from audited CSV."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).parent
CSV_PATH = ROOT / "data" / "ca_grocery_stores_audited.csv"
MAP_PATH = ROOT / "data" / "ca_grocer_map_data.json"


def store_id_to_key(store_id: str) -> str:
    return store_id.rsplit("|", 1)[-1]


def main() -> None:
    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        audit = {
            r["Store #"]: r
            for r in csv.DictReader(f)
            if r.get("Store #")
        }

    with MAP_PATH.open(encoding="utf-8") as f:
        data = json.load(f)

    updated = 0
    for store in data["stores"]:
        key = store_id_to_key(store.get("id", ""))
        row = audit.get(key)
        if not row:
            continue
        if row.get("Normalized_Banner"):
            store["banner"] = row["Normalized_Banner"]
        if row.get("Normalized_Banner_Group"):
            store["banner_group"] = row["Normalized_Banner_Group"]
        if row.get("Web_URL"):
            store["web_url"] = row["Web_URL"]
        updated += 1

    MAP_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Updated {updated} stores from audit CSV.")


if __name__ == "__main__":
    main()
