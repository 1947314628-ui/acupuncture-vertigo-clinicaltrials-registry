#!/usr/bin/env python3
"""
Complete fetch: targeted search (35 query pairs) + broad vertigo search.
Saves raw_studies.json (targeted) and all_vertigo_studies.json (broad).
"""
import requests, json, time, os
from datetime import datetime

OUTPUT_DIR = r"D:\Desktop\针灸眩晕NLP分析论文\data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

BASE_URL = "https://clinicaltrials.gov/api/v2/studies"
COND_TERMS = ["vertigo", "dizziness", "vertiginous", "dizzy", "Meniere"]
INTR_TERMS = ["acupuncture", "electroacupuncture", "acupoint", "moxibustion",
              "acupressure", "auricular acupuncture", "ear acupuncture"]

def fetch_all_studies(term_query, label):
    """Fetch ALL studies for a query term, handling pagination."""
    studies = []
    params = {
        "query.term": term_query,
        "pageSize": 100,
        "format": "json",
    }
    next_token = None
    page = 0

    while True:
        page += 1
        if next_token:
            params["pageToken"] = next_token

        try:
            resp = requests.get(BASE_URL, params=params, timeout=90)
        except Exception as e:
            print(f"  [ERROR] {label} page {page}: {e}")
            break

        if resp.status_code != 200:
            print(f"  [ERROR] {label} page {page}: HTTP {resp.status_code}")
            break

        data = resp.json()
        batch = data.get('studies', [])
        if not batch:
            break

        studies.extend(batch)
        next_token = data.get('nextPageToken')
        if not next_token:
            break
        time.sleep(0.35)  # Rate limiting between pages

    print(f"  {label}: {len(studies)} studies ({page} pages)")
    return studies

# ═══════════════════════════════════════════════════════
# PART 1: Targeted combinatorial search
# ═══════════════════════════════════════════════════════
print("=" * 60)
print("PART 1: Targeted Combinatorial Search")
print(f"Condition terms ({len(COND_TERMS)}): {COND_TERMS}")
print(f"Intervention terms ({len(INTR_TERMS)}): {INTR_TERMS}")
print(f"Total query pairs: {len(COND_TERMS) * len(INTR_TERMS)}")
print("=" * 60)

targeted_studies = {}  # nct_id -> study
total_raw = 0

for i, cond in enumerate(COND_TERMS):
    for j, intr in enumerate(INTR_TERMS):
        query = f"{cond} {intr}"
        label = f"[{i*len(INTR_TERMS)+j+1}/35] {cond} + {intr}"

        batch = fetch_all_studies(query, label)
        for study in batch:
            try:
                nct_id = study['protocolSection']['identificationModule']['nctId']
            except (KeyError, TypeError):
                continue
            if nct_id not in targeted_studies:
                targeted_studies[nct_id] = study
        total_raw += len(batch)
        time.sleep(0.25)  # Rate limiting between queries

print(f"\nTargeted search complete:")
print(f"  Total raw results: {total_raw}")
print(f"  Unique NCT IDs: {len(targeted_studies)}")

# Save targeted results
targeted_list = list(targeted_studies.values())
with open(os.path.join(OUTPUT_DIR, "raw_studies.json"), 'w', encoding='utf-8') as f:
    json.dump(targeted_list, f, ensure_ascii=False)
print(f"  Saved: raw_studies.json ({os.path.getsize(os.path.join(OUTPUT_DIR, 'raw_studies.json')) / 1024:.1f} KB)")

# ═══════════════════════════════════════════════════════
# PART 2: Broad vertigo search (denominator for 6.2%)
# ═══════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("PART 2: Broad Vertigo Search")
print("=" * 60)

BROAD_QUERY = "vertigo OR dizziness OR Meniere"
print(f"Query: {BROAD_QUERY}")

broad_studies = {}
batch = fetch_all_studies(BROAD_QUERY, "Broad vertigo")
for study in batch:
    try:
        nct_id = study['protocolSection']['identificationModule']['nctId']
    except (KeyError, TypeError):
        continue
    if nct_id not in broad_studies:
        broad_studies[nct_id] = study

print(f"\nBroad search complete:")
print(f"  Total raw results: {len(batch)}")
print(f"  Unique NCT IDs: {len(broad_studies)}")

# Save broad results
broad_list = list(broad_studies.values())
with open(os.path.join(OUTPUT_DIR, "all_vertigo_studies.json"), 'w', encoding='utf-8') as f:
    json.dump(broad_list, f, ensure_ascii=False)
print(f"  Saved: all_vertigo_studies.json ({os.path.getsize(os.path.join(OUTPUT_DIR, 'all_vertigo_studies.json')) / 1024:.1f} KB)")

# ═══════════════════════════════════════════════════════
# PART 3: Merge and deduplicate for combined unique count
# ═══════════════════════════════════════════════════════
combined = {}
for nct_id, study in targeted_studies.items():
    combined[nct_id] = study
for nct_id, study in broad_studies.items():
    if nct_id not in combined:
        combined[nct_id] = study

print(f"\nCombined unique studies: {len(combined)}")

# Save metadata
meta = {
    "fetch_date": datetime.now().isoformat(),
    "condition_terms": COND_TERMS,
    "intervention_terms": INTR_TERMS,
    "targeted_unique": len(targeted_studies),
    "broad_unique": len(broad_studies),
    "combined_unique": len(combined),
    "targeted_raw_total": total_raw,
    "broad_raw_total": len(batch),
    "broad_query": BROAD_QUERY,
    "method": "Multi-query term search + broad vertigo search with NCT ID deduplication",
}
with open(os.path.join(OUTPUT_DIR, "fetch_metadata.json"), 'w', encoding='utf-8') as f:
    json.dump(meta, f, ensure_ascii=False, indent=2)

print(f"\nAll data saved to {OUTPUT_DIR}")
print("Done.")
