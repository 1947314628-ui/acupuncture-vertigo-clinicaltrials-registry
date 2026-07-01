#!/usr/bin/env python3
"""Final entity counts for manuscript, using verified acupuncture studies only."""
import json, re, sys, io
from collections import Counter
import numpy as np

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DATA_DIR = r"D:\Desktop\针灸眩晕NLP分析论文\data"
with open(f"{DATA_DIR}/all_labeled_studies.json", 'r', encoding='utf-8') as f:
    all_studies = json.load(f)

# Keyword-based classification
acu_v = [s for s in all_studies if s['is_acu_vertigo']]

# Conservative filter: require acupuncture method OR acupoint to be present
verified = [s for s in acu_v if s.get('acu_methods') or s.get('acu_points')]
false_positives = len(acu_v) - len(verified)

print(f'{"="*60}')
print(f'FINAL ENTITY COUNTS FOR MANUSCRIPT')
print(f'{"="*60}')
print(f'API search date: 2026-07-01')
print(f'Total vertigo studies in ClinicalTrials.gov: {len(all_studies)}')
print(f'Keyword-positive (acupuncture + vertigo): {len(acu_v)} ({len(acu_v)/len(all_studies)*100:.1f}%)')
print(f'Verified (has method or acupoint): {len(verified)} ({len(verified)/len(all_studies)*100:.1f}%)')
print(f'Likely false positives removed: {false_positives}')
print()

def normalize_acupoint(pt):
    m = re.match(r'^([A-Z]+\d+)\(', pt)
    if m: return m.group(1)
    if re.match(r'^[A-Z]+\d+$', pt): return pt
    return pt

# --- ACUPOINTS ---
all_pts = []
for s in verified:
    normalized = set()
    for pt in s.get('acu_points', []):
        normalized.add(normalize_acupoint(pt))
    all_pts.extend(normalized)
pt_cnt = Counter(all_pts)
n_pts = sum(1 for s in verified if s.get('acu_points'))
print(f'--- ACUPOINTS ({n_pts}/{len(verified)} studies, {sum(pt_cnt.values())} occurrences) ---')
for p, c in pt_cnt.most_common(25):
    print(f'  {p}: {c}')

# --- METHODS ---
all_methods = []
for s in verified:
    all_methods.extend(s.get('acu_methods', []))
method_cnt = Counter(all_methods)
n_method = sum(1 for s in verified if s.get('acu_methods'))
print(f'\n--- ACUPUNCTURE METHODS ({n_method}/{len(verified)} studies, {sum(method_cnt.values())} occurrences) ---')
for m, c in method_cnt.most_common():
    print(f'  {m}: {c}')

# --- CONTROL TYPES ---
all_ctrl = []
for s in verified:
    all_ctrl.extend(s.get('control_types', []))
ctrl_cnt = Counter(all_ctrl)
print(f'\n--- CONTROL TYPES ---')
for c, n in ctrl_cnt.most_common():
    print(f'  {c}: {n}')

# --- VERTIGO SUBTYPES ---
all_sub = []
for s in verified:
    all_sub.extend(s.get('vertigo_subtypes', []))
sub_cnt = Counter(all_sub)
n_sub = sum(1 for s in verified if s.get('vertigo_subtypes'))
print(f'\n--- VERTIGO SUBTYPES ({n_sub}/{len(verified)} studies) ---')
for st, n in sub_cnt.most_common():
    print(f'  {st}: {n}')

# --- OUTCOME MEASURES ---
all_out = []
for s in verified:
    all_out.extend(s.get('outcome_measures', []))
out_cnt = Counter(all_out)
print(f'\n--- OUTCOME MEASURES ---')
for o, n in out_cnt.most_common():
    print(f'  {o}: {n}')

# --- STATUS ---
status_cnt = Counter(s.get('overall_status', '') for s in verified)
print(f'\n--- STATUS ({sum(status_cnt.values())} total) ---')
for s, c in status_cnt.most_common():
    print(f'  {s}: {c} ({c/len(verified)*100:.1f}%)')

# --- COUNTRIES ---
country_cnt = Counter()
for s in verified:
    if s.get('countries'):
        for c in s['countries'].split('; '):
            if c.strip(): country_cnt[c.strip()] += 1
print(f'\n--- TOP COUNTRIES ---')
for c, n in country_cnt.most_common(10):
    print(f'  {c}: {n}')

# --- ENROLLMENT ---
enrolls = sorted([s['enrollment_count'] for s in verified if s.get('enrollment_count') and s['enrollment_count'] > 0])
print(f'\n--- ENROLLMENT ---')
print(f'  N with data: {len(enrolls)}')
print(f'  Median: {np.median(enrolls):.0f}')
print(f'  IQR: {np.percentile(enrolls,25):.0f}-{np.percentile(enrolls,75):.0f}')
print(f'  Range: {min(enrolls)}-{max(enrolls)}')

# --- YEARS ---
years = [s['year'] for s in verified if s.get('year')]
print(f'\n--- YEAR RANGE: {min(years)}-{max(years)} ---')
yc = Counter(years)
for y in sorted(yc):
    print(f'  {y}: {yc[y]}')

# Save verified NCT IDs for reference
print(f'\nVerified NCT IDs:')
for s in verified:
    methods = '; '.join(s.get('acu_methods', []))
    pts = '; '.join(s.get('acu_points', []))[:60]
    print(f'  {s["nct_id"]} ({s["year"]}): methods=[{methods}], pts=[{pts}]')
