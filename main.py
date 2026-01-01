import json
import unicodedata
import uuid

CITIES_INPUT = "./cities15000.txt"
COUNTRIES_INPUT = "./countries.json"
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


# --- Load country lookup ---
with open(COUNTRIES_INPUT, "r", encoding="utf-8") as f:
    countries = json.load(f)

country_lookup = {
    c["abbreviation"]: c["country"]
    for c in countries
    if "abbreviation" in c and "country" in c
}


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

        country_name = country_lookup.get(country_code, "")
        if not country_name:
            continue

        # --- Build search string ---
        folded = ascii_fold(name)

        search_tokens = {
            name.lower(),
            folded.lower(),
            country_name.lower(),
        }

        search_tokens = {t for t in search_tokens if t}
        search = " ".join(sorted(search_tokens))

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
