#!/usr/bin/env python3
"""Split unverified Lucky rows into distinct banner subgroups."""
import csv
import re
from pathlib import Path

REPO = Path(__file__).parent
CSV_PATH = REPO / "data" / "ca_grocery_stores_audited.csv"


def clean_for_group(name: str) -> str:
    """Remove store numbers and suffixes to get a display group name."""
    s = name.strip()
    s = re.sub(r"(?<=[a-zA-Z])'S\b", "'s", s)
    s = s.replace("’", "'")
    # Remove "#" before numbers (e.g. "Lucky #7 Food Store" -> "Lucky 7 Food Store")
    s = re.sub(r"#(?=\d)", "", s)
    # Remove trailing #number, number, or codes like "Inc. 3", "LLC 2"
    s = re.sub(r"\s*#?\d+(?:[-\s][A-Z]{1,5})?\s*$", "", s, flags=re.IGNORECASE)
    s = re.sub(r"\s+[-#]?[A-Z]{1,5}\s*$", "", s)
    # Strip organizational suffixes
    s = re.sub(r"\s+(?:Inc\.?|LLC|L\.L\.C\.|Ltd\.?|Co\.?|Corp\.?|Company)\s*$", "", s, flags=re.IGNORECASE)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def split_lucky(rows: list[dict]) -> tuple[list[dict], dict]:
    changes: dict[tuple[str, str], int] = {}
    for r in rows:
        group = (r.get("Normalized_Banner_Group") or "").strip()
        status = (r.get("Verified_Status") or "").strip()
        banner = (r.get("Normalized_Banner") or "").strip() or (r.get("Banner") or "").strip()

        if not banner.lower().startswith("lucky"):
            continue
        if status == "verified - active chain":
            continue
        if group == "Lucky 7 Supermarket":
            continue

        # The three San Jose "Lucky 7 Supermarket" / "Lucky 7 King" stores share
        # lucky7super.com (confirmed via official site locations). Group them together.
        if "lucky 7" in banner.lower() and ("supermarket" in banner.lower() or "king" in banner.lower()):
            new_group = "Lucky 7 Supermarket"
            if not r.get("Web_URL") or "lucky7super" not in r["Web_URL"]:
                r["Web_URL"] = "https://lucky7super.com/"
            r["Verified_Status"] = "verified - active chain"
        else:
            new_group = clean_for_group(banner)
            if not new_group:
                new_group = banner

        # If already in the correct distinct banner group, skip.
        if new_group == group:
            continue

        if new_group != group:
            changes.setdefault((group, new_group), 0)
            changes[(group, new_group)] += 1
            r["Normalized_Banner_Group"] = new_group
            r["Normalized_Banner"] = new_group

    return rows, changes


def main() -> None:
    with CSV_PATH.open(newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    fieldnames = list(rows[0].keys()) if rows else []

    rows, changes = split_lucky(rows)

    with CSV_PATH.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {CSV_PATH}")
    print("Changes:")
    for (old, new), c in sorted(changes.items(), key=lambda x: -x[1]):
        print(f"  {c:4d}  {old!r}  ->  {new!r}")


if __name__ == "__main__":
    main()
