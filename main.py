import json
import unicodedata
import uuid

CITIES_INPUT = "./cities15000.txt"
COUNTRIES_INPUT = "./countries.json"
TIMEZONE_ALIASES_INPUT = "./timezone_search_aliases.json"
OUTPUT_PATH = "./cities100000_with_country.json"


def ascii_fold(text: str) -> str:
    """
    Convert unicode text to a best-effort ASCII equivalent.
    Example: 'Samandağ' -> 'Samandag'
    """
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(
        c for c in normalized
        if not unicodedata.combining(c) and ord(c) < 128
    )


def dedupe_preserve_order(items):
    """
    Deduplicate a list while preserving first occurrence order.
    """
    seen = set()
    result = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            result.append(item)
    return result


# --- Load country lookup ---
with open(COUNTRIES_INPUT, "r", encoding="utf-8") as f:
    countries = json.load(f)

country_lookup = {
    c["abbreviation"]: c["country"]
    for c in countries
    if "abbreviation" in c and "country" in c
}


# --- Load timezone search aliases ---
with open(TIMEZONE_ALIASES_INPUT, "r", encoding="utf-8") as f:
    TIMEZONE_SEARCH_ALIASES = json.load(f)


results = []

# --- Stream cities file ---
with open(CITIES_INPUT, "r", encoding="utf-8") as infile:
    for line in infile:
        parts = line.rstrip("\n").split("\t")

        if len(parts) < 18:
            continue

        name = parts[1]
        feature_code = parts[7]
        country_code = parts[8]
        timezone = parts[17]

        try:
            population = int(parts[14])
        except ValueError:
            continue

        # Include if large city OR capital (covers microstates)
        if population <= 100_000 and feature_code != "PPLC":
            continue

        country_name = country_lookup.get(country_code)
        if not country_name:
            continue

        folded = ascii_fold(name)

        # ------------------------------------------------------------------
        # Build ordered search tokens (priority matters!)
        # ------------------------------------------------------------------

        search_parts = []

        # 1️⃣ Timezone aliases (highest intent: EDT, EST, Eastern Time, etc.)
        tz_aliases = TIMEZONE_SEARCH_ALIASES.get(timezone, [])
        for alias in tz_aliases:
            search_parts.append(alias.lower())

        # 2️⃣ City name (exact + ASCII-folded)
        search_parts.append(name.lower())
        if folded.lower() != name.lower():
            search_parts.append(folded.lower())

        # 3️⃣ Country name (lowest intent)
        search_parts.append(country_name.lower())

        # Deduplicate while preserving order
        search_parts = dedupe_preserve_order(search_parts)

        search = " ".join(search_parts)

        results.append({
            "id": str(uuid.uuid4()),
            "city": name,
            "country": country_name,
            "timezone": timezone,
            "search": search,
        })


# --- Write final output ---
with open(OUTPUT_PATH, "w", encoding="utf-8") as outfile:
    json.dump(results, outfile, ensure_ascii=False, separators=(",", ":"))

print(f"Wrote {len(results)} rows to {OUTPUT_PATH}")
