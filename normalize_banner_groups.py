#!/usr/bin/env python3
"""Normalize retailer banner groups and banners in ca_grocery_stores_audited.csv.

This script canonicalizes chain names, reassigns Misc. and mis-grouped rows by
official Web_URL domain, clusters independent stores that share a real domain,
merges obvious typo variants, and updates Normalized_Banner to the canonical
chain name for matched rows.
"""
from __future__ import annotations

import csv
import difflib
import re
from collections import Counter, defaultdict
from pathlib import Path

from update_cmab_logos import (
    GENERIC,
    canonical,
    domain_from_url,
    is_directory,
    sig,
    tokenize,
)

REPO = Path(__file__).parent
CSV_PATH = REPO / "data" / "ca_grocery_stores_audited.csv"

# Rename known miscased / truncated groups.
GROUP_OVERRIDES = {
    "Baby'S Nutrition": "Baby Nutrition",
    "Baby'S Nutritional Center": "Baby Nutritional Care",
    "Coconut Hill Ch": "Coconut Hill",
    "Ray'S Food Place": "Ray's Food Place",
    "Trader Joe'S": "Trader Joe's",
    "Gelson'S Market": "Gelson's Market",
    "Lunardi'S Market": "Lunardi's Market",
    "Tony'S Market": "Tony's Market",
    "Sam'S Club": "Sam's Club",
    "Sam'S Market": "Sam's Market",
    "Raley'S": "Raley's",
    "Mother'S Nutritional Center": "Mother's Nutritional Center",
    "Mother'S Market": "Mother's Market",
    "Mother'S Nutritonal Center": "Mother's Nutritional Center",
}

# Canonical group names for official domains. This also fixes bad mappings
# from the old CHAIN_WEBSITES dict (e.g. lucky.pt).
DOMAIN_OVERRIDES = {
    "99ranch.com": "99 Ranch Market",
    "aldi.us": "Aldi",
    "albertsons.com": "Albertsons",
    "asiamartsr.com": "Asian Market",
    "arteagas.com": "Arteagas Food Center",
    "babynutritionshop.com": "Baby Nutrition",
    "baronsmarket.com": "Barons Market",
    "berkeleybowl.com": "Berkeley Bowl",
    "bigsaverfoods.com": "Big Saver Foods",
    "biritemarket.com": "Bi-Rite Market",
    "briarpatch.coop": "Briarpatch Co-op",
    "bristolfarms.com": "Bristol Farms",
    "cardenasmarkets.com": "Cardenas",
    "carnicerialacarreta.com": "Carniceria La Carreta",
    "carnivalsupermarkets.com": "Carnival Market",
    "costco.com": "Costco Wholesale",
    "costlessfoods.com": "Cost Less Foods",
    "coconuthill.com": "Coconut Hill",
    "dollargeneral.com": "Dollar General Market",
    "elsupermarkets.com": "El Super",
    "eurekanaturalfoods.com": "Eureka Natural Foods",
    "food4less.com": "Food 4 Less",
    "foodmaxx.com": "Food Maxx",
    "frazierfarmsmarket.com": "Frazier Farms Market",
    "freshcofoodcenter.com": "Freshco Food Center",
    "gardenfarmsmarket.com": "Garden Farms Market",
    "gelsons.com": "Gelson's Market",
    "groceryoutlet.com": "Grocery Outlet",
    "gdlmeatmarkets.com": "Guadalajara Market",
    "gw-supermarket.com": "GW Supermarket",
    "hamiltoneuromarkets.com": "Hamilton Euromarket",
    "hardestersmarkets.com": "Hardester's Markets",
    "islandpacificmarket.com": "Island Pacific Supermarket",
    "jacksons.com": "Jacksons Food Stores",
    "jimbos.com": "Jimbo's",
    "jonsmarketplace.com": "Jons Market",
    "kidsnutricarestore.com": "Kids Nutricare",
    "lamexicana-mercado.com": "La Mexicana Market",
    "laaguilamarket.com": "La Aguila Market",
    "laprincesamarket.net": "La Princesa Market",
    "lareynameatmarket.com": "La Reyna Meat Market",
    "lasespuelas.us": "Las Espuelas",
    "lassens.com": "Lassens",
    "lazyacres.com": "Lazy Acres",
    "luckysupermarkets.com": "Lucky",
    "lucky.pt": "Lucky",
    "marukai.com": "Marukai",
    "maxifoodsmarkets.com": "Maxi Foods Markets",
    "miranchosupermarket.com": "Mi Rancho Market",
    "mothersmarket.com": "Mother's Market",
    "mothersnc.com": "Mother's Nutritional Center",
    "newleaf.com": "New Leaf Community Market",
    "nobhill.com": "Nob Hill Foods",
    "northcoast.coop": "North Coast Co-op",
    "northparkproduce.com": "North Park Produce",
    "nuggetmarket.com": "Nugget Market",
    "oliversmarket.com": "Oliver's Market",
    "orlandosmarket.com": "Orlando's Market",
    "raleys.com": "Raley's",
    "ralphs.com": "Ralphs",
    "rranchmarkets.com": "R-Ranch Market",
    "safeway.com": "Safeway",
    "samsclub.com": "Sam's Club",
    "santacruzmarkets.com": "Santa Cruz Market",
    "santafefoods.org": "Santa Fe Foods",
    "savemart.com": "Save Mart",
    "seafoodcity.com": "Seafood City Supermarket",
    "sevenseasca.com": "Seven Seas Gourmet Foods",
    "smartandfinal.com": "Smart & Final",
    "sprouts.com": "Sprouts Farmers Market",
    "staterbros.com": "Stater Bros. Market",
    "statefoods.net": "State Foods Supermarket",
    "streetcorner.com": "Street Corner",
    "superafoods.com": "Super A Foods",
    "superiorgrocers.com": "Superior Grocers",
    "superkingmarkets.com": "Super King Market",
    "supermercadomitierra.com": "Mi Tierra Market",
    "target.com": "Target",
    "thecornermarket.com": "Corner Market",
    "tokyocentral.com": "Tokyo Central",
    "traderjoes.com": "Trader Joe's",
    "tsemporium.com": "T&S Emporium",
    "unitedmarkets.com": "United Market",
    "vallartasupermarkets.com": "Vallarta Supermarket",
    "vons.com": "Vons",
    "vivasupermarket.com": "Viva Market",
    "walmart.com": "Walmart",
    "wincofoods.com": "Winco Foods",
    "woodlandsmarket.com": "Woodlands Market",
    "wholefoodsmarket.com": "Whole Foods Market",
    "sunrisenaturalfoods.net": "Sunrise Natural Foods",
}

# Chains that are real but do not have an official domain in the current CSV.
# They are still allowed to absorb Misc. rows by exact banner startswith.
KNOWN_NO_DOMAIN_CHAINS = {
    "H Mart",
    "Ray's Food Place",
    "Foods Co",
    "Pavilions",
    "Bel Air",
    "Primetime Nutrition",
    "Mother Earth Nutrition",
    "Basic Nutrition",
    "Sam's Market",
    "Zion Market",
}

# Chain groups whose name is a common word or is easily confused with generic
# banners; do not allow "contains"/fuzzy expansion beyond "Group <number>".
STRICT_STARTS_GROUPS = {
    "Lucky",
    "Foods Co",
    "El Super",
    "La Mexicana Market",
    "Baby Nutrition",
    "Save Mart",
    "La Princesa Market",
}

# Specific banner strings whose group is known to be wrong and should be corrected.
BANNER_GROUP_OVERRIDES = {
    "H Food Mart": "Misc.",
    "H Food Mart #8": "Misc.",
    "Baby Nutritional Care": "Baby Nutritional Care",
    "Baby's Nutritional Center": "Baby Nutritional Care",
    "Babys Nutrition Center": "Baby Nutritional Care",
    "Baby's Nutrition Care": "Baby Nutritional Care",
    "Baby Nutrition Shop": "Baby Nutrition",
    "Baby Nutrition": "Baby Nutrition",
    "Baby's Nutrition": "Baby Nutrition",
    "Babys Nutrition": "Baby Nutrition",
    # Catch "Costco Murrieta 1390" and similar banners that do not include
    # the word "Wholesale" but clearly belong to the Costco chain.
    "Costco": "Costco Wholesale",
}

# Non-chain groups that are too generic or ambiguous to absorb Misc. rows by banner alone.
NON_EXPANDABLE = {
    "A Mart",
    "Al's Market",
    "Azteca Market",
    "Brothers Market",
    "Central Market",
    "City Market",
    "Corner Market",
    "El Mercado",
    "El Torito Market",
    "Express Mart",
    "Farmers Market",
    "Fiesta Market",
    "First Step Nutrition",
    "Food Mart",
    "Foodnet Supermarket",
    "Foothill Market",
    "Fresh Produce",
    "Hernandez Market",
    "International Market",
    "John's Market",
    "Kings Market",
    "La Familia Market",
    "La Favorita Market",
    "La Hacienda Market",
    "La Morenita Market",
    "Lakeside Market",
    "Lee's Market",
    "Los Amigos Market",
    "Los Portales",
    "Los Primos Market",
    "Lucky 7",
    "Lucky Market",
    "Mi Ranchito Market",
    "Mi Tiendita",
    "Mountain Market",
    "Neighborhood Market",
    "One Stop Market",
    "Perez Market",
    "Plaza Market",
    "Prince Market",
    "Quality Market",
    "Ranch Market",
    "Rainbow Market",
    "Royal Market",
    "Sierra Minit Mart",
    "Star Market",
    "Sunshine Market",
    "Tower Market",
    "Valley Market",
    "Verdugo Market",
    "Village Market",
    "Young's Market",
}

WEB_URL_FIXES = {
    "Lucky": {
        "old": {"lucky.pt"},
        "new": "https://www.luckysupermarkets.com",
    },
}


def row_domain(row: dict) -> str:
    return domain_from_url(row.get("Web_URL", ""))


def standardize(name: str) -> str:
    return canonical(name)


def display_name_from_lcp(banners: list[str]) -> str | None:
    if not banners:
        return None
    s = banners[0]
    for t in banners[1:]:
        i = 0
        while i < len(s) and i < len(t) and s[i].lower() == t[i].lower():
            i += 1
        s = s[:i]
    s = s.rstrip(" -#&,.:;/")
    s = re.sub(r"\s+(Inc\.?|LLC\.?|Co\.?|Company)\s*$", "", s, flags=re.I)
    s = s.strip(" -#&,.:;/")
    if len(s) < 3:
        return None
    return standardize(s)


def title_case_tokens(s: str) -> str:
    parts = []
    for tok in re.split(r"[^a-zA-Z0-9']+", s):
        if not tok:
            continue
        if re.fullmatch(r"[0-9]+", tok):
            parts.append(tok)
        elif re.fullmatch(r"[A-Z]{2,}", tok):
            parts.append(tok)
        elif len(tok) <= 2 and tok.isalpha():
            parts.append(tok.upper())
        else:
            parts.append(tok.capitalize())
    return " ".join(parts)


def domain_core_name(domain: str) -> str:
    if not domain:
        return ""
    core = domain.split(".")[0]
    parts = re.split(r"[-_]+", core)
    return title_case_tokens(" ".join(parts))


def clean_banner(name: str) -> str:
    """Remove trailing store numbers / location codes while preserving brand numbers."""
    if not name:
        return ""
    # " #5-Corcora", " 703", " BK" (uppercase code, with or without preceding number)
    s = re.sub(r"\s*#?\d+(?:[-\s][A-Z]{1,5})?\s*$", "", name)
    s = re.sub(r"\s+[-#]?[A-Z]{1,5}\s*$", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def stem(t: str) -> str:
    """Very light stemmer for plural / adjectival forms."""
    if len(t) > 3 and t.endswith("s"):
        t = t[:-1]
    if len(t) > 4 and t.endswith("al"):
        t = t[:-2]
    return t


def _token_prefix_match(group: str, banner: str) -> bool:
    """Return True if the banner's tokens begin with the group's tokens (stemmed).

    Leading generic words ("the", "el", etc.) are skipped in the banner.
    Extra trailing tokens are allowed, so a banner like
    "Arteagas Food Center (Santa Clara)" matches the group "Arteagas Food Center",
    but "Nature's Whole Food Depot" does not match "Whole Foods Market" because the
    group tokens are not at the start.
    """
    LEADING_SKIP = {
        "a", "an", "the", "and", "of", "for", "in", "on", "at", "by", "with",
    }
    g_toks = tokenize(group)
    if not g_toks:
        return False
    c_toks = tokenize(clean_banner(banner))
    start = 0
    while start < len(c_toks) and c_toks[start] in LEADING_SKIP:
        start += 1
    if start >= len(c_toks):
        return False
    if stem(c_toks[start]) != stem(g_toks[0]):
        return False
    for i, gt in enumerate(g_toks[1:], start=1):
        if start + i >= len(c_toks):
            return False
        if stem(c_toks[start + i]) != stem(gt):
            return False
    return True


def is_chain(info: dict, group_name: str) -> bool:
    """Return True if a group is a known chain that can absorb matching Misc. rows."""
    if group_name in KNOWN_NO_DOMAIN_CHAINS:
        return True
    domain = info.get("domain")
    if not domain:
        return False
    dom_count = info.get("domain_count", 0)
    count = info.get("count", 0)
    if dom_count >= 3 or (count and dom_count / count >= 0.5):
        return True
    return False


def is_prefix_substring(candidate: str, current: str) -> bool:
    """Return True if candidate is a shorter prefix/sub-chain of current."""
    if not candidate or not current or candidate == current:
        return False
    c_low = candidate.lower()
    cur_low = current.lower()
    if cur_low.startswith(c_low + " "):
        return True
    if re.search(r"(?<![a-z0-9])" + re.escape(c_low) + r"(?![a-z0-9])", cur_low):
        return True
    return False


def _strict_start_match(group: str, banner: str) -> bool:
    """Exact match or "Group <number>" / "Group California <number>" only."""
    clean = clean_banner(banner)
    g_low = group.lower()
    c_low = clean.lower()
    return bool(re.match(rf"^{re.escape(g_low)}(?:\\s+\\d+|\\s+ california\\s+\\d+)?$", c_low))


def group_matches_banner(group: str, banner: str, chain: bool) -> bool:
    """Return True when a row banner belongs to the candidate group."""
    if not group or not banner:
        return False
    clean = clean_banner(banner)
    g_low = group.lower()
    c_low = clean.lower()

    # Chains with distinctive multi-word names can match anywhere in the banner
    # (e.g. "Ceres Grocery Outlet", "Mini Mars Grocery Outlet").
    if chain and group not in STRICT_STARTS_GROUPS:
        if re.search(r"(?<![a-z0-9])" + re.escape(g_low) + r"(?![a-z0-9])", c_low):
            return True

    # Exact match always wins.
    if c_low == g_low:
        return True

    # Non-chain generic groups should not absorb "X Group Y" variants.
    if not chain and group in NON_EXPANDABLE:
        return False

    # Raw starts-with match.
    if c_low.startswith(g_low + " "):
        if group in STRICT_STARTS_GROUPS:
            return _strict_start_match(group, banner)
        return True

    # Fuzzy token-prefix match (handles plural/adjective forms and trailing
    # descriptors, but only when the group tokens are at the start of the banner).
    if _token_prefix_match(group, banner):
        if group in STRICT_STARTS_GROUPS:
            return _strict_start_match(group, banner)
        return True

    return False


def build_canonical_groups(rows: list[dict]) -> dict[str, dict]:
    """Build canonical group metadata keyed by standardized group name."""
    groups: dict[str, dict] = {}
    for domain, group in DOMAIN_OVERRIDES.items():
        group = standardize(group)
        if group not in groups:
            groups[group] = {"domain": None, "domain_count": 0, "count": 0, "from_override": True}

    by_group: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        g = standardize(r.get("Normalized_Banner_Group", "").strip() or "Misc.")
        if g in GROUP_OVERRIDES:
            g = GROUP_OVERRIDES[g]
        by_group[g].append(r)

    for g, rs in by_group.items():
        if g == "Misc.":
            continue
        dom_counts = Counter()
        for r in rs:
            d = row_domain(r)
            if d and not is_directory(r.get("Web_URL", "")):
                dom_counts[d] += 1
        top_domain, top_count = dom_counts.most_common(1)[0] if dom_counts else (None, 0)

        if g in groups:
            info = groups[g]
            if top_domain and not info.get("domain"):
                info["domain"] = top_domain
                info["domain_count"] = top_count
            info["count"] += len(rs)
        else:
            groups[g] = {
                "domain": top_domain,
                "domain_count": top_count,
                "count": len(rs),
                "from_override": False,
            }

    # Ensure all groups are represented.
    for g, rs in by_group.items():
        if g not in groups:
            groups[g] = {"domain": None, "domain_count": 0, "count": len(rs), "from_override": False}

    return groups


def cluster_misc_by_domain(rows: list[dict]) -> dict[str, str]:
    """Return domain -> new group name for Misc. stores that share an official domain."""
    misc_by_domain: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        if standardize(r.get("Normalized_Banner_Group", "").strip() or "") == "Misc.":
            d = row_domain(r)
            if d and not is_directory(r.get("Web_URL", "")):
                misc_by_domain[d].append(r)

    domain_group: dict[str, str] = {}
    for d, rs in misc_by_domain.items():
        if d in DOMAIN_OVERRIDES:
            domain_group[d] = standardize(DOMAIN_OVERRIDES[d])
            continue
        if len(rs) < 2:
            continue
        banners = [r.get("Normalized_Banner", "").strip() or r.get("Banner", "").strip() for r in rs]
        lcp = display_name_from_lcp(banners)
        if lcp and len(tokenize(lcp)) >= 1:
            group = standardize(lcp)
        else:
            group = standardize(domain_core_name(d))
        if len(tokenize(group)) == 0 or group.lower() in {"natural", "market", "foods", "store", "shop"}:
            group = standardize(domain_core_name(d))
        domain_group[d] = group
    return domain_group


def choose_group(row: dict, canonical_groups: dict[str, dict], domain_group: dict[str, str]) -> str | None:
    current = standardize(row.get("Normalized_Banner_Group", "").strip() or "Misc.")
    banner = (row.get("Normalized_Banner", "").strip() or row.get("Banner", "").strip())
    for override_banner, override_group in BANNER_GROUP_OVERRIDES.items():
        if banner.lower() == override_banner.lower() or banner.lower().startswith(override_banner.lower() + " "):
            return standardize(override_group)
    web_url = (row.get("Web_URL", "") or "").strip()
    domain = row_domain(row)
    if current in GROUP_OVERRIDES:
        current = GROUP_OVERRIDES[current]

    candidates = []

    # 1. Domain-based candidates (strong signal).
    if domain and not is_directory(web_url):
        if domain in DOMAIN_OVERRIDES:
            target = standardize(DOMAIN_OVERRIDES[domain])
            if group_matches_banner(target, banner, is_chain(canonical_groups.get(target, {}), target)):
                candidates.append((target, "domain"))
        for g, info in canonical_groups.items():
            if info.get("domain") == domain and group_matches_banner(g, banner, is_chain(info, g)):
                candidates.append((g, "domain"))
        if domain in domain_group and current == "Misc.":
            target = domain_group[domain]
            if group_matches_banner(target, banner, True):
                candidates.append((target, "domain"))

    # 2. Banner-only candidates for rows without a usable domain.
    # Only allow chain/known groups to absorb Misc. rows by banner; local
    # non-chain groups are surfaced in the report for manual review instead.
    if not candidates and current == "Misc.":
        for g, info in canonical_groups.items():
            if g == current:
                continue
            chain = is_chain(info, g)
            if not (chain or g in KNOWN_NO_DOMAIN_CHAINS):
                continue
            if group_matches_banner(g, banner, chain):
                candidates.append((g, "banner"))

    if not candidates:
        return None

    def score(item):
        g, reason = item
        info = canonical_groups.get(g, {})
        tok_score = len(set(sig(tokenize(g))) & set(sig(tokenize(clean_banner(banner)))))
        order = {"domain": 0, "banner": 1}
        return (order.get(reason, 9), -tok_score, -info.get("count", 0), g)

    candidates.sort(key=score)
    chosen = candidates[0][0]

    # Protect a current canonical group from being collapsed into a shorter prefix.
    if current in canonical_groups and chosen != current and is_prefix_substring(chosen, current):
        return None
    return chosen


def merge_typo_groups(groups: dict[str, dict]) -> dict[str, str]:
    """Merge groups that are almost-certain typo variants of one another."""
    names = sorted(groups, key=lambda n: -groups[n]["count"])
    mapping = {}
    for a in names:
        if a in mapping:
            continue
        for b in names:
            if b in mapping or a == b:
                continue
            ratio = difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()
            if ratio >= 0.92:
                canonical_target = a if groups[a]["count"] >= groups[b]["count"] else b
                old = b if canonical_target == a else a
                mapping[old] = canonical_target
    return mapping


def clean_web_url(row: dict, new_group: str) -> str | None:
    fix = WEB_URL_FIXES.get(new_group)
    if not fix:
        return None
    current = (row.get("Web_URL", "") or "").lower()
    if any(old in current for old in fix["old"]):
        return fix["new"]
    return None


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--csv", type=Path, default=CSV_PATH)
    args = parser.parse_args()

    rows = list(csv.DictReader(args.csv.open(newline="", encoding="utf-8-sig")))
    fieldnames = list(rows[0].keys()) if rows else []

    # Pre-apply group renames.
    for r in rows:
        g = standardize(r.get("Normalized_Banner_Group", "").strip() or "Misc.")
        if g in GROUP_OVERRIDES:
            r["Normalized_Banner_Group"] = GROUP_OVERRIDES[g]
        else:
            r["Normalized_Banner_Group"] = g

    canonical_groups = build_canonical_groups(rows)
    domain_group = cluster_misc_by_domain(rows)

    # Add newly-discovered domain clusters to the canonical set as chains.
    for d, g in domain_group.items():
        if g not in canonical_groups:
            canonical_groups[g] = {
                "domain": d,
                "domain_count": sum(1 for r in rows if row_domain(r) == d and standardize(r.get("Normalized_Banner_Group", "") or "") == "Misc."),
                "count": 0,
                "from_override": True,
            }

    # Typo merge pass.
    typo_map = merge_typo_groups(canonical_groups)
    for old, new in typo_map.items():
        for r in rows:
            if standardize(r.get("Normalized_Banner_Group", "")) == old:
                r["Normalized_Banner_Group"] = new

    # Rebuild after typo merges.
    canonical_groups = build_canonical_groups(rows)
    for d, g in domain_group.items():
        if g not in canonical_groups:
            canonical_groups[g] = {"domain": d, "domain_count": 0, "count": 0, "from_override": True}

    changes = Counter()
    for r in rows:
        target = choose_group(r, canonical_groups, domain_group)
        current = standardize(r.get("Normalized_Banner_Group", "").strip() or "Misc.")
        if not target or target == current:
            r["Normalized_Banner"] = canonical(r.get("Normalized_Banner", ""))
            continue
        changes[(current, target)] += 1
        r["Normalized_Banner_Group"] = target
        fixed = clean_web_url(r, target)
        if fixed:
            r["Web_URL"] = fixed

    for r in rows:
        r["Normalized_Banner"] = canonical(r.get("Normalized_Banner", ""))

    print(f"Rows processed: {len(rows)}")
    print(f"Unique groups after normalization: {len(set(r['Normalized_Banner_Group'] for r in rows))}")
    print(f"Changes made: {sum(changes.values())}")
    print("Top 25 changes:")
    for (old, new), c in changes.most_common(25):
        print(f"  {c:4d}  {old!r}  ->  {new!r}")

    if args.apply:
        with args.csv.open("w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f"Wrote {args.csv}")
    else:
        print("Dry run. Use --apply to write changes.")


if __name__ == "__main__":
    main()
