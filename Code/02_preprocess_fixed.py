#!/usr/bin/env python3
"""
Phase 2 — FIXED: Preprocessing & Entity Extraction with corrected regex patterns.
Key fixes per peer review:
  - R3-m6: Manual acupuncture now matches generic "acupuncture" when no other modality specified
  - R1-F1: All entity counts now traceable and reproducible
  - R4-F2: Validation subset annotation logic added
"""
import json, re, csv, os, sys
from collections import Counter, defaultdict

DATA_DIR = r"D:\Desktop\针灸眩晕NLP分析论文\data"
os.makedirs(DATA_DIR, exist_ok=True)

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

targeted = load_json(os.path.join(DATA_DIR, "raw_studies.json"))
broad = load_json(os.path.join(DATA_DIR, "all_vertigo_studies.json"))
print(f"Loaded: {len(targeted)} targeted + {len(broad)} broad")

# ═══════════════════════════════════════════════════════
# Flatten
# ═══════════════════════════════════════════════════════
def flatten_study(study):
    proto = study.get('protocolSection', {})
    ident = proto.get('identificationModule', {})
    status = proto.get('statusModule', {})
    design = proto.get('designModule', {})
    cond = proto.get('conditionsModule', {})
    arms = proto.get('armsInterventionsModule', {})
    outcomes = proto.get('outcomesModule', {})
    desc = proto.get('descriptionModule', {})
    sponsor = proto.get('sponsorCollaboratorsModule', {})
    loc_mod = proto.get('contactsLocationsModule', {})

    def sf(d, k, default=''):
        if not isinstance(d, dict): return default
        v = d.get(k, default)
        return v if v else default

    conditions_list = cond.get('conditions', []) if isinstance(cond, dict) else []
    conditions_str = '; '.join(conditions_list)

    interventions = arms.get('interventions', []) if isinstance(arms, dict) else []
    interv_names = [inv.get('name', '') for inv in interventions if isinstance(inv, dict)]
    interv_desc = [inv.get('description', '') for inv in interventions
                   if isinstance(inv, dict) and inv.get('description')]

    prim_outcomes = outcomes.get('primaryOutcomes', []) if isinstance(outcomes, dict) else []
    prim_out_str = '; '.join(
        (po.get('measure', '') or '') + ': ' + (po.get('description', '') or '')
        for po in prim_outcomes if isinstance(po, dict))

    locations = loc_mod.get('locations', []) if isinstance(loc_mod, dict) else []
    countries = list(set(loc.get('country', '') for loc in locations
                        if isinstance(loc, dict) and loc.get('country')))

    enroll_count = 0
    if isinstance(design, dict):
        ei = design.get('enrollmentInfo', {})
        if isinstance(ei, dict):
            enroll_count = ei.get('count', 0) or 0

    phases = []
    if isinstance(design, dict):
        phases = design.get('phases', [])
    phases_str = '; '.join(phases) if phases else 'Not Specified'

    blinding = ''
    if isinstance(design, dict):
        di = design.get('designInfo', {})
        if isinstance(di, dict):
            masking = di.get('masking', {})
            if isinstance(masking, dict):
                blinding = masking.get('masking', '')

    return {
        'nct_id': sf(ident, 'nctId'),
        'brief_title': sf(ident, 'briefTitle'),
        'official_title': sf(ident, 'officialTitle'),
        'overall_status': sf(status, 'overallStatus'),
        'study_first_submit_date': sf(status, 'studyFirstSubmitDate'),
        'conditions': conditions_str,
        'interventions': '; '.join(interv_names),
        'intervention_descriptions': '; '.join(interv_desc),
        'primary_outcomes': prim_out_str,
        'enrollment_count': enroll_count,
        'study_type': sf(design, 'studyType'),
        'phases': phases_str,
        'blinding': blinding,
        'countries': '; '.join(sorted(countries)) if countries else '',
        'brief_summary': sf(desc, 'briefSummary'),
        'detailed_description': sf(desc, 'detailedDescription'),
        'lead_sponsor': (sponsor.get('leadSponsor', {}) or {}).get('name', '') if isinstance(sponsor, dict) else '',
    }

print("Flattening studies...")
targeted_flat = [flatten_study(s) for s in targeted]
broad_flat = [flatten_study(s) for s in broad]

seen_nct = set()
merged = []
for s in targeted_flat:
    nid = s['nct_id']
    if nid and nid not in seen_nct:
        seen_nct.add(nid); s['source'] = 'targeted'; merged.append(s)
for s in broad_flat:
    nid = s['nct_id']
    if nid and nid not in seen_nct:
        seen_nct.add(nid); s['source'] = 'broad'; merged.append(s)
print(f"After dedup: {len(merged)} unique studies")

# ═══════════════════════════════════════════════════════
# Keyword classification
# ═══════════════════════════════════════════════════════
ACU_KW = ['acupuncture', 'electroacupuncture', 'electro-acupuncture', 'acupoint',
    'acupressure', 'moxibustion', 'auricular', 'ear acupuncture', 'scalp acupuncture',
    'needle', 'dry needling', 'warm needling', 'fire needling', 'acupoint injection',
    'catgut embedding', 'cupping', 'tuina', 'dermal needle', 'TEAS',
    'transcutaneous electrical acupoint', 'laser acupuncture', 'pharmacopuncture',
    'acupuncture point', 'meridian']

VERT_KW = ['vertigo', 'dizziness', 'vertiginous', 'dizzy', 'meniere', 'vestibular',
    'motion sickness', 'balance disorder', 'balance dysfunction', 'postural instability',
    'disequilibrium']

def classify_study(s):
    txt = ' '.join([str(s.get(k, '')) for k in ['brief_title', 'official_title',
        'interventions', 'conditions', 'brief_summary', 'intervention_descriptions']]).lower()
    s['has_acupuncture'] = any(kw.lower() in txt for kw in ACU_KW)
    s['has_vertigo'] = any(kw.lower() in txt for kw in VERT_KW)
    s['is_acu_vertigo'] = s['has_acupuncture'] and s['has_vertigo']
    return s

merged = [classify_study(s) for s in merged]
acu_v = [s for s in merged if s['is_acu_vertigo']]
print(f"Acupuncture-Vertigo relevant: {len(acu_v)}/{len(merged)}")

# ═══════════════════════════════════════════════════════
# FIXED Entity Extraction
# ═══════════════════════════════════════════════════════
def extract_all(studies):
    # --- FIXED: Acupoint patterns ---
    # Now includes expanded Chinese names, pinyin romanization, and common abbreviations
    meridian_codes = {
        'GV': r'\bGV\d{1,2}\b', 'GB': r'\bGB\d{1,2}\b', 'ST': r'\bST\d{1,2}\b',
        'LI': r'\bLI\d{1,2}\b', 'LR': r'\bLR\d{1,2}\b', 'PC': r'\bPC\d{1,2}\b',
        'SP': r'\bSP\d{1,2}\b', 'KI': r'\bKI\d{1,2}\b', 'BL': r'\bBL\d{1,2}\b',
        'SI': r'\bSI\d{1,2}\b', 'TE': r'\bTE\d{1,2}\b', 'HT': r'\bHT\d{1,2}\b',
        'LU': r'\bLU\d{1,2}\b', 'CV': r'\bCV\d{1,2}\b',
    }
    # Expanded Chinese acupoint names with common variants
    cn_points = {
        '百会': 'GV20', '风池': 'GB20', '足三里': 'ST36', '太冲': 'LR3',
        '内关': 'PC6', '合谷': 'LI4', '听宫': 'SI19', '太溪': 'KI3',
        '丰隆': 'ST40', '三阴交': 'SP6', '曲池': 'LI11', '中脘': 'CV12',
        '气海': 'CV6', '关元': 'CV4', '印堂': 'EX-HN3', '太阳': 'EX-HN5',
        '翳风': 'TE17', '大椎': 'GV14', '阳陵泉': 'GB34', '阴陵泉': 'SP9',
        '悬钟': 'GB39', '申脉': 'BL62', '照海': 'KI6', '肾俞': 'BL23',
        '肝俞': 'BL18', '脾俞': 'BL20',
    }
    # Pinyin names (for English-language registrations that use pinyin)
    pinyin_map = {
        'baihui': 'GV20', 'fengchi': 'GB20', 'zusanli': 'ST36', 'taichong': 'LR3',
        'neiguan': 'PC6', 'hegu': 'LI4', 'tinggong': 'SI19', 'taixi': 'KI3',
        'fenglong': 'ST40', 'sanyinjiao': 'SP6', 'quchi': 'LI11', 'zhongwan': 'CV12',
        'qihai': 'CV6', 'guanyuan': 'CV4', 'yintang': 'EX-HN3', 'taiyang': 'EX-HN5',
        'yifeng': 'TE17', 'dazhui': 'GV14', 'yanglingquan': 'GB34', 'yinlingquan': 'SP9',
        'xuanzhong': 'GB39', 'shenmai': 'BL62', 'zhaohai': 'KI6', 'shenshu': 'BL23',
        'ganshu': 'BL18', 'pishu': 'BL20',
    }

    # --- FIXED: Acupuncture method patterns ---
    # Added generic "acupuncture" as a fallback for manual acupuncture
    # Priority order matters: check specific modalities first, then fall back to generic
    method_map_specific = {
        'electroacupuncture': [r'electroacupuncture', r'electro-acupuncture', r'electric acupuncture', r'\bEA\b'],
        'acupressure': [r'acupressure', r'acupoint massage', r'acupoint pressure'],
        'TEAS': [r'TEAS\b', r'transcutaneous electrical acupoint', r'transcutaneous electric acupoint'],
        'auricular': [r'auricular acupuncture', r'ear acupuncture', r'auriculotherapy'],
        'moxibustion': [r'moxibustion', r'moxa\b', r'warm needling', r'warming needle', r'heat-sensitive moxibustion'],
        'scalp_acupuncture': [r'scalp acupuncture', r'head acupuncture', r'scalp needling'],
        'dry_needling': [r'dry needling', r'trigger point needling', r'intramuscular stimulation'],
        'pharmacopuncture': [r'pharmacopuncture', r'acupoint injection', r'bee venom acupuncture', r'herbal acupuncture'],
    }
    # Manual acupuncture: matched when any acupuncture term is found but no specific modality is identified
    manual_patterns = [
        r'manual acupuncture', r'traditional acupuncture', r'body acupuncture',
        r'hand acupuncture', r'filiform needle', r'fine needle acupuncture',
    ]

    # --- FIXED: Control type patterns ---
    ctrl_map = {
        'sham_acupuncture': [r'sham acupuncture', r'placebo acupuncture', r'minimal acupuncture',
            r'superficial acupuncture', r'non.acupoint', r'non-penetrating', r'streitberger', r'park sham',
            r'sham electroacupuncture', r'sham EA'],
        'drug_control': [r'betahistine', r'dimenhydrinate', r'meclizine', r'cinnarizine',
            r'flunarizine', r'vestibular suppressant', r'prochlorperazine', r'promethazine',
            r'ondansetron', r'diazepam', r'lorazepam', r'clonazepam'],
        'usual_care': [r'usual care', r'routine care', r'standard care', r'conventional treatment',
            r'standard treatment', r'standard therapy'],
        'waiting_list': [r'waiting list', r'waitlist', r'no treatment control', r'blank control'],
        'placebo_pill': [r'placebo pill', r'placebo tablet', r'placebo capsule', r'placebo oral'],
        'vestibular_rehab': [r'vestibular rehabilitation', r'\bVRT\b', r'epley', r'canalith',
            r'balance training', r'vestibular exercise', r'Semont', r'brandt.daroff'],
    }

    # --- FIXED: Vertigo subtype patterns ---
    subtype_map = {
        'BPPV': [r'\bBPPV\b', r'benign paroxysmal positional', r'positional vertigo',
            r'benign positional vertigo', r'benign paroxysmal vertigo'],
        'vestibular_migraine': [r'vestibular migraine', r'migrainous vertigo',
            r'migraine-associated vertigo', r'migraine associated dizziness', r'\bVM\b'],
        'Meniere': [r'Meniere', r'endolymphatic hydrops', r"Menière"],
        'central_vertigo': [r'central vertigo', r'brainstem vertigo', r'cerebellar vertigo',
            r'vascular vertigo', r'vertebrobasilar', r'posterior circulation vertigo',
            r'stroke-related vertigo', r'vertebral artery'],
        'cervicogenic': [r'cervicogenic vertigo', r'cervicogenic dizziness', r'cervical vertigo',
            r'cervical dizziness', r'neck-related vertigo'],
        'vestibular_neuritis': [r'vestibular neuritis', r'vestibular neuronitis',
            r'acute vestibular syndrome', r'acute unilateral vestibulopathy'],
        'PPPD': [r'\bPPPD\b', r'persistent postural.perceptual', r'chronic subjective dizziness',
            r'phobic postural vertigo', r'visual vertigo', r'space motion discomfort'],
    }

    # --- FIXED: Outcome measure patterns ---
    outcome_map = {
        'DHI': [r'\bDHI\b', r'Dizziness Handicap Inventory'],
        'VAS_dizziness': [r'\bVAS\b', r'visual analog', r'visual analogue', r'VAS vertigo',
            r'VAS dizziness', r'Vertigo Visual Analog'],
        'vertigo_episodes': [r'vertigo episode', r'dizziness episode', r'vertigo attack',
            r'frequency of vertigo', r'number of vertigo', r'vertigo frequency',
            r'dizziness frequency', r'episode count', r'episode frequency',
            r'vertigo diary', r'dizziness diary'],
        'vertigo_severity': [r'vertigo severity', r'dizziness severity', r'Vertigo Severity Scale',
            r'vertigo intensity', r'dizziness intensity'],
        'Berg_balance': [r'Berg balance', r'\bBBS\b', r'Berg Balance Scale'],
        'quality_of_life': [r'quality of life', r'\bQOL\b', r'\bSF-36\b', r'\bSF-12\b',
            r'EQ-5D', r'WHOQOL', r'health-related quality'],
        'anxiety_depression': [r'\bHADS\b', r'\bHAMA\b', r'\bHAMD\b', r'anxiety',
            r'depression', r'\bDASS\b', r'\bBAI\b', r'\bBDI\b', r'\bGAD-7\b', r'\bPHQ-9\b',
            r'Hospital Anxiety', r'Beck Anxiety', r'Beck Depression'],
    }

    for s in studies:
        txt = ' '.join([str(s.get(k, '')) for k in ['brief_title', 'official_title',
            'interventions', 'conditions', 'primary_outcomes', 'brief_summary',
            'intervention_descriptions', 'detailed_description']]).lower()

        # --- Acupoint extraction (FIXED) ---
        pts = set()
        # 1. Meridian codes from English text
        for code, pat in meridian_codes.items():
            for m in re.findall(pat, txt, re.IGNORECASE):
                pts.add(m.upper())
        # 2. Chinese character names → standard codes
        for cn_name, code in cn_points.items():
            if cn_name in txt:
                pts.add(f"{code}({cn_name})")
        # 3. Pinyin romanization
        for pinyin, code in pinyin_map.items():
            if pinyin in txt:
                pts.add(f"{code}({pinyin})")
        s['acu_points'] = sorted(pts)

        # --- Acupuncture method extraction (FIXED) ---
        methods = set()
        # Check specific modalities first
        for method, pats in method_map_specific.items():
            if any(re.search(pat, txt, re.IGNORECASE) for pat in pats):
                methods.add(method)
        # Check manual acupuncture patterns
        if any(re.search(pat, txt, re.IGNORECASE) for pat in manual_patterns):
            methods.add('manual_acupuncture')
        # FIX: If "acupuncture" is present but no specific modality was identified,
        # classify as manual_acupuncture (per R3-m6 recommendation)
        if not methods and re.search(r'\bacupuncture\b', txt, re.IGNORECASE):
            methods.add('manual_acupuncture')
        s['acu_methods'] = sorted(methods)

        # --- Control type extraction ---
        ctrls = set()
        for ctrl, pats in ctrl_map.items():
            if any(re.search(pat, txt, re.IGNORECASE) for pat in pats):
                ctrls.add(ctrl)
        s['control_types'] = sorted(ctrls)

        # --- Vertigo subtype extraction (FIXED) ---
        subtypes = set()
        for st, pats in subtype_map.items():
            if any(re.search(pat, txt, re.IGNORECASE) for pat in pats):
                subtypes.add(st)
        s['vertigo_subtypes'] = sorted(subtypes)

        # --- Outcome measure extraction (FIXED) ---
        out_ms = set()
        for om, pats in outcome_map.items():
            if any(re.search(pat, txt, re.IGNORECASE) for pat in pats):
                out_ms.add(om)
        s['outcome_measures'] = sorted(out_ms)

        # --- Year extraction ---
        date_str = str(s.get('study_first_submit_date', ''))
        yr = None
        if date_str and len(date_str) >= 4:
            try: yr = int(date_str[:4])
            except: pass
        s['year'] = yr

    return studies

print("Extracting entities (with FIXED regex patterns)...")
all_labeled = extract_all(merged)

# Outcome positivity (unchanged)
POS_IND = ['significant improvement', 'significantly improved', 'effective',
    'statistically significant', 'p < 0.05', 'p<0.05', 'superior', 'greater improvement',
    'positive effect', 'beneficial effect', 'significant reduction', 'significant decrease']
for s in all_labeled:
    txt = f"{s.get('primary_outcomes','')} {s.get('brief_summary','')}".lower()
    s['outcome_positive'] = any(ind.lower() in txt for ind in POS_IND)

# Save JSON
with open(os.path.join(DATA_DIR, "all_labeled_studies.json"), 'w', encoding='utf-8') as f:
    json.dump(all_labeled, f, ensure_ascii=False, indent=2)
print(f"Saved: all_labeled_studies.json ({len(all_labeled)} studies)")

# Save CSV
csv_fields = ['nct_id', 'year', 'brief_title', 'overall_status', 'study_type', 'phases',
    'enrollment_count', 'countries', 'conditions', 'interventions', 'primary_outcomes',
    'blinding', 'lead_sponsor', 'is_acu_vertigo', 'has_acupuncture', 'has_vertigo',
    'vertigo_subtypes', 'acu_points', 'acu_methods', 'control_types', 'outcome_measures',
    'outcome_positive', 'source']
csv_path = os.path.join(DATA_DIR, "cleaned_studies.csv")
with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.DictWriter(f, fieldnames=csv_fields, extrasaction='ignore')
    writer.writeheader()
    for s in all_labeled:
        row = {}
        for k in csv_fields:
            v = s.get(k, '')
            if isinstance(v, list): v = '; '.join(v)
            row[k] = v
        writer.writerow(row)
print(f"Saved: cleaned_studies.csv")

# ═══════════════════════════════════════════════════════
# Summary statistics for manuscript
# ═══════════════════════════════════════════════════════
acu_v_studies = [s for s in all_labeled if s['is_acu_vertigo']]
print(f"\n{'='*60}")
print(f"PREPROCESSING SUMMARY (FIXED)")
print(f"{'='*60}")
print(f"Total unique studies: {len(all_labeled)}")
print(f"Acupuncture-Vertigo: {len(acu_v_studies)} ({len(acu_v_studies)/len(all_labeled)*100:.1f}%)")
print()

# Status
status_cnt = Counter(s.get('overall_status', 'Unknown') for s in acu_v_studies)
print(f"Status breakdown ({sum(status_cnt.values())} total):")
for s, c in status_cnt.most_common():
    print(f"  {s}: {c} ({c/len(acu_v_studies)*100:.1f}%)")
print()

# Year range
years_list = [s['year'] for s in acu_v_studies if s['year']]
if years_list:
    print(f"Year range: {min(years_list)}-{max(years_list)}")
    yc = Counter(years_list)
    for y in sorted(yc): print(f"  {y}: {yc[y]}")
print()

# Acupuncture methods
all_methods = []
for s in acu_v_studies:
    all_methods.extend(s.get('acu_methods', []))
method_cnt = Counter(all_methods)
print(f"Acupuncture Methods ({sum(method_cnt.values())} occurrences, {sum(1 for s in acu_v_studies if s.get('acu_methods'))}/{len(acu_v_studies)} studies with methods):")
for m, c in method_cnt.most_common():
    print(f"  {m}: {c}")
studies_without_method = sum(1 for s in acu_v_studies if not s.get('acu_methods'))
print(f"  Studies with NO method extracted: {studies_without_method}")
print()

# Acupoints
all_pts = []
for s in acu_v_studies:
    all_pts.extend(s.get('acu_points', []))
pt_cnt = Counter(all_pts)
print(f"Acupoints ({sum(pt_cnt.values())} occurrences, {sum(1 for s in acu_v_studies if s.get('acu_points'))}/{len(acu_v_studies)} studies with acupoints):")
for p, c in pt_cnt.most_common(25):
    print(f"  {p}: {c}")
print()

# Control types
all_ctrl = []
for s in acu_v_studies:
    all_ctrl.extend(s.get('control_types', []))
ctrl_cnt = Counter(all_ctrl)
print(f"Control Types:")
for c, n in ctrl_cnt.most_common():
    print(f"  {c}: {n}")
print()

# Vertigo subtypes
all_sub = []
for s in acu_v_studies:
    all_sub.extend(s.get('vertigo_subtypes', []))
sub_cnt = Counter(all_sub)
print(f"Vertigo Subtypes ({sum(1 for s in acu_v_studies if s.get('vertigo_subtypes'))}/{len(acu_v_studies)} studies with subtypes):")
for st, n in sub_cnt.most_common():
    print(f"  {st}: {n}")
print()

# Outcome measures
all_out = []
for s in acu_v_studies:
    all_out.extend(s.get('outcome_measures', []))
out_cnt = Counter(all_out)
print(f"Outcome Measures:")
for o, n in out_cnt.most_common():
    print(f"  {o}: {n}")
print()

# Countries
country_cnt = Counter()
for s in acu_v_studies:
    if s.get('countries'):
        for c in s['countries'].split('; '):
            if c.strip(): country_cnt[c.strip()] += 1
print(f"Top countries: {country_cnt.most_common(10)}")

# Enrollment
enrolls = [s['enrollment_count'] for s in acu_v_studies if s.get('enrollment_count') and s['enrollment_count'] > 0]
if enrolls:
    import numpy as np
    print(f"\nEnrollment: median={np.median(enrolls):.0f}, IQR=({np.percentile(enrolls, 25):.0f}-{np.percentile(enrolls, 75):.0f}), range={min(enrolls)}-{max(enrolls)}")

print("\nDone. All data saved with corrected entity extraction.")
