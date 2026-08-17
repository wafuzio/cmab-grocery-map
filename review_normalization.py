#!/usr/bin/env python3
"""Produce a human-readable report of proposed banner-group normalization changes."""
import csv
import shutil
from collections import defaultdict
from pathlib import Path

import normalize_banner_groups as n

CSV_PATH = Path(__file__).parent / "data" / "ca_grocery_stores_audited.csv"

def main():
    shutil.copy(CSV_PATH, "/tmp/orig.csv")
    rows = list(csv.DictReader(open("/tmp/orig.csv", newline="", encoding="utf-8-sig")))
    for r in rows:
        g = n.standardize(r.get("Normalized_Banner_Group", "").strip() or "Misc.")
        if g in n.GROUP_OVERRIDES:
            g = n.GROUP_OVERRIDES[g]
        r["Normalized_Banner_Group"] = g

    canonical = n.build_canonical_groups(rows)
    domain_group = n.cluster_misc_by_domain(rows)
    for d, g in domain_group.items():
        if g not in canonical:
            canonical[g] = {"domain": d, "domain_count": 0, "count": 0, "from_override": True}

    changes = defaultdict(list)
    for r in rows:
        target = n.choose_group(r, canonical, domain_group)
        current = n.standardize(r.get("Normalized_Banner_Group", "").strip() or "Misc.")
        if target and target != current:
            changes[(current, target)].append(r)

    total = sum(len(v) for v in changes.values())
    print(f"Total proposed changes: {total}")
    print(f"Unique group-pair changes: {len(changes)}")
    for (old, new), rs in sorted(changes.items(), key=lambda x: -len(x[1])):
        print(f"\n{len(rs):4d}  {old!r}  ->  {new!r}")
        for r in rs[:5]:
            print(f"       {r['Store #']} | {r.get('Banner','')} | {r.get('Web_URL','')}")
        if len(rs) > 5:
            print(f"       ... and {len(rs) - 5} more")


if __name__ == "__main__":
    main()
