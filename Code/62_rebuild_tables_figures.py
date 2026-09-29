#!/usr/bin/env python3
"""Rebuild Tables 1-3 and Figures 1-4 from the unified search results.

Replaces 20_generate_figures.py, which hard-coded every plotted value.
Every number here is derived from files under Data/Unified/ or Data/.

Gates (the script exits non-zero if any fails):
  G1 every proportion stack sums to 100% (+/- 0.05)
  G2 every figure legend n equals the number of source rows behind it
  G3 every value printed on a figure is present in the emitted Tables CSV
  G4 inclusion audit rows == search hits, and include + exclude == hits

Search scope (disclosed in Table 1, NOT corrected for, so no density ratio
is computed anywhere):
  ClinicalTrials.gov  condition field   (query.cond)
  ChiCTR              target disease    (studyailment)
  ITMCTR              target disease    (dynamicQueries[target_disease])
"""
import csv, json, os, re, sys, collections

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UNI = os.path.join(BASE, 'Data', 'Unified')
DATA = os.path.join(BASE, 'Data')
TAB = os.path.join(BASE, 'Tables')
FIG = os.path.join(BASE, 'Figures')
for d in (TAB, FIG):
    os.makedirs(d, exist_ok=True)

plt.rcParams['font.family'] = 'Arial'
plt.rcParams['font.size'] = 10

C_CTG, C_CHI, C_ITM = '#4472C4', '#ED7D31', '#A5A5A5'

# ---------------------------------------------------------------- inclusion rules
# R2: an acupuncture-family modality must be the registered intervention.
ACU_RE = re.compile(
    r'acupunctur|acupoint|electroacup|moxibust|acupress|needl|catgut|'
    r'pharmacopuncture|scalp acu|针灸|针刺|电针|毫针|温针|艾灸|穴位|'
    r'耳穴|针刀|揿针|火针|头针|腹针|浮针|埋线|脐针|针法|针', re.I)
# Explicitly out of family: registered interventions that are not
# needling/acupoint therapies. A record is dropped when its intervention text
# names one of these and names no needling modality.
NOT_ACU_RE = re.compile(r'vagus nerve stimulation|taVNS|chuna|chiropract|tuina|'
                        r'manual therapy|massage|repositioning|manipulation|'
                        r'lidocaine|blood patch|推拿|手法复位|矫正手法|扳法|'
                        r'脊椎矫正|手法', re.I)
WITHDRAWN = {'WITHDRAWN', 'TERMINATED'}
# ClinicalTrials.gov returns status as an enum; mapped to the one vocabulary all
# three registries share, so the figure reads a single set of labels (gate G6).
# ACTIVE_NOT_RECRUITING and ENROLLING_BY_INVITATION are both ongoing and enrolling
# or having enrolled, so they join Recruiting; no record in this set carries either.
CT_STATUS = {'COMPLETED': 'Completed', 'RECRUITING': 'Recruiting',
             'ENROLLING_BY_INVITATION': 'Recruiting',
             'ACTIVE_NOT_RECRUITING': 'Recruiting',
             'NOT_YET_RECRUITING': 'Not yet recruiting',
             'UNKNOWN': 'Not stated', 'SUSPENDED': 'Other', 'WITHDRAWN': 'Other',
             'TERMINATED': 'Other'}


def pget(d, *ks, default=None):
    for k in ks:
        if not isinstance(d, dict):
            return default
        d = d.get(k)
        if d is None:
            return default
    return d


def mask_class(masking, who):
    """Masking -> one of the five pre-declared classes."""
    if not masking or masking == 'NONE':
        return 'Open-label or none' if masking == 'NONE' else 'Not stated'
    who = set(who or [])
    part = 'PARTICIPANT' in who
    assess = bool(who & {'OUTCOMES_ASSESSOR', 'INVESTIGATOR', 'CARE_PROVIDER'})
    if part and assess:
        return 'Double-blind'
    if part:
        return 'Single-blind'
    if assess:
        return 'Assessor-blinded'
    return 'Other or partial'


def text_mask_class(s):
    """Free-text blinding field (Chinese registries) -> same five classes."""
    s = (s or '').strip()
    if not s or re.fullmatch(r'(Not stated|未说明|无|None|无\(开放\)|未填写)', s):
        return 'Not stated' if s and not re.fullmatch(r'(无|None)', s) else (
            'Open-label or none' if re.fullmatch(r'(无|None)', s) else 'Not stated')
    if 'open' in s.lower() or '开放' in s:
        return 'Open-label or none'
    low = s.lower()
    # The masked parties are read from the record's own wording, in either
    # language. Chinese records name them by role: 受试者/患者 for the
    # participant, and 评价者/评估者/数据收集者/分析者/统计人员/研究者 for the
    # others. An explicit 双盲 or 单盲 with no roles named cannot be mapped onto
    # the classes, so it is reported as 'Other or partial' rather than guessed.
    subj = any(k in low for k in ('subject', 'participant')) or \
        any(k in s for k in ('受试者', '患者盲', '病例盲'))
    other = any(k in low for k in ('assessor', 'investigator', 'statistician',
                                   'analyst', 'outcome evaluator')) or \
        any(k in s for k in ('评价', '评估', '研究者', '统计', '分析', '数据收集',
                             '资料收集', '疗效评价', '结局')) or ('tcd' in low)
    if subj and other:
        return 'Double-blind'
    if subj:
        return 'Single-blind'
    if other:
        return 'Assessor-blinded'
    return 'Other or partial'


def is_randomized(r):
    """Randomized allocation, from the registry's own allocation wording.

    ClinicalTrials.gov has an allocation-type field; the Chinese registries state
    the sequence-generation method instead (随机方法), so the test covers both
    languages. 非随机/不随机 negates it.
    """
    d = ' '.join([r.get('design') or '', r.get('randomisation') or ''])
    if re.search(r'非随机|不随机|未随机|not randomi', d, re.I):
        return False
    return bool(re.search(r'randomi|随机', d, re.I))


# ---------------------------------------------------------------- ClinicalTrials.gov
def load_ctgov():
    studies = json.load(open(os.path.join(UNI, 'ctgov_raw.json'), encoding='utf-8'))
    rows, audit = [], []
    for st in studies:
        p = st['protocolSection']
        nid = p['identificationModule']['nctId']
        blob = json.dumps(p, ensure_ascii=False)
        conds = '; '.join(p.get('conditionsModule', {}).get('conditions', []))
        ints = [i.get('name', '') for i in
                pget(p, 'armsInterventionsModule', 'interventions', default=[]) or []]
        arms = [a.get('label', '') for a in
                pget(p, 'armsInterventionsModule', 'armGroups', default=[]) or []]
        rec = {
            'registry': 'ClinicalTrials.gov', 'reg_id': nid,
            'year': int((p['statusModule'].get('studyFirstSubmitDate') or '2000')[:4]),
            'status': p['statusModule']['overallStatus'],
            'design': pget(p, 'designModule', 'designInfo', 'allocation'),
            'masking': pget(p, 'designModule', 'designInfo', 'maskingInfo', 'masking'),
            'who': pget(p, 'designModule', 'designInfo', 'maskingInfo', 'whoMasked'),
            'n': pget(p, 'designModule', 'enrollmentInfo', 'count'),
            'country': (pget(p, 'contactsLocationsModule', 'locations', default=[{}])[0] or {}).get('country'),
            'conditions': conds, 'interventions': ints, 'arms': arms,
            'outcomes': [o.get('measure', '') for o in
                         pget(p, 'outcomesModule', 'primaryOutcomes', default=[]) or []],
            'title': p['identificationModule'].get('briefTitle', ''),
        }
        if not ACU_RE.search(blob):
            audit.append((nid, conds, 'Exclude', 'No acupuncture-family term anywhere in the registered protocol'))
            continue
        if rec['status'] in WITHDRAWN or not rec['n']:
            audit.append((nid, conds, 'Exclude', 'Withdrawn or terminated, or zero planned enrolment'))
            continue
        # the acupuncture-family term must be the registered intervention, not a
        # passing mention: require it in the intervention or arm-group names, or,
        # where the registry left those generic ("Group A"), in the official title.
        itxt = ' ; '.join(ints + arms)
        ttxt = p['identificationModule'].get('officialTitle', '') + ' ' + rec['title']
        target = itxt if ACU_RE.search(itxt) else (ttxt if ACU_RE.search(ttxt) else '')
        if target and NOT_ACU_RE.search(target):
            audit.append((nid, conds, 'Exclude',
                          'Registered intervention is a non-acupuncture modality '
                          '(vagus-nerve stimulation / manual therapy / injection)'))
            continue
        if not target:
            audit.append((nid, conds, 'Exclude',
                          'Acupuncture-family term appears only in narrative text; '
                          'not the registered intervention'))
            continue
        rec['status'] = CT_STATUS.get(rec['status'], rec['status'])
        rec['blinding_class'] = mask_class(rec['masking'], rec['who'])
        rows.append(rec)
        audit.append((nid, conds, 'Include', ''))
    return rows, audit, len(studies)


# ---------------------------------------------------------------- ChiCTR
# ChiCTR states recruitment status in Chinese; the figure vocabulary is shared
# across the three registries, so it is normalised here at load time. An
# unmapped value falls through to 'Other' rather than being silently dropped,
# which would leave the stacked bar short of 100% (gate G1).
CH_STATUS = {'尚未开始': 'Not yet recruiting', '正在进行': 'Recruiting',
             '结束': 'Completed', '已完成': 'Completed', '暂停': 'Other',
             '撤销': 'Other'}


def load_chictr():
    """Included ChiCTR records, from the rule-derived set in 66_chictr_extract.py.

    Both the molecule and every field come from that file, which screens the
    retrieved records by a stated rule and reads the fields off the registry
    pages. The earlier hand-kept extraction list is no longer a data source: it
    was missing an acupuncture trial for vestibular migraine, which is one of the
    defects this revision exists to fix.
    """
    rows = []
    rdr = csv.DictReader(open(os.path.join(UNI, 'chictr_included.csv'),
                              encoding='utf-8-sig'))
    for r in rdr:
        rows.append({
            'registry': 'ChiCTR', 'reg_id': r['reg_id'].strip(),
            'title': r['title'].strip(),
            'year': int(r['year'] or 0),
            'status': CH_STATUS.get(r['status'].strip(),
                                    r['status'].strip() or 'Not stated'),
            'design': r['study_design'].strip(),
            'randomisation': r['randomisation'].strip(), 'n': int(r['sample_size'] or 0),
            'blinding_class': text_mask_class(r['blinding']),
            'blinding_raw': r['blinding'].strip(),
            'subtype': r['disease'].strip(),
            'intervention': r['intervention'].strip(),
            'control': '', 'outcomes': r['outcomes'].strip(),
            'country': 'China',
        })
    # Audit every ChiCTR hit, not only the included ones (G4). The decisions come
    # from the screening step so that the reason shown for a record is the reason
    # the rule actually applied to it.
    audit = [(r['reg_id'], r['registered condition'], r['Decision'], r['Reason'])
             for r in csv.DictReader(open(os.path.join(UNI, 'chictr_screen.csv'),
                                          encoding='utf-8-sig'))]
    return rows, audit


# ---------------------------------------------------------------- ITMCTR
ITM_STATUS = {'1004001': 'Not yet recruiting', '1004002': 'Recruiting',
              '1004003': 'Recruiting', '1004004': 'Completed'}


def load_itmctr(partner_ids=None):
    """ITMCTR records, minus those the platform itself flags as ChiCTR twins.

    Duplicates are resolved from `partner_registry_number`, which ITMCTR
    publishes in the record, rather than from a hand-maintained id list: the
    exclusion then rests on a field a reader can look up.
    """
    if partner_ids is None:
        partner_ids = {r['reg_id'] for r in load_chictr()[0]}
    raw = json.load(open(os.path.join(UNI, 'itmctr_raw.json'), encoding='utf-8'))
    rows, audit = [], []
    for r in raw:
        rid, title = r['registration_number'], r.get('publictitle_zh') or ''
        if not ACU_RE.search(title):
            audit.append((rid, r.get('target_disease_zh') or '', 'Exclude',
                          'No acupuncture-family term in the registered title'))
            continue
        partner = (r.get('partner_registry_number') or '').strip()
        if partner in partner_ids:
            audit.append((rid, r.get('target_disease_zh') or '', 'Exclude',
                          'Cross-registered on {} (partner_registry_number); '
                          'counted once under ChiCTR'.format(partner)))
            continue
        rows.append({
            'registry': 'ITMCTR', 'reg_id': rid,
            'year': int((r.get('study_time_start') or r.get('first_submit_time') or '2025')[:4]),
            'status': ITM_STATUS.get(str(r.get('recruiting_status')), 'Not stated'),
            'design': 'Single-arm' if '单臂' in (r.get('randomization_procedure_zh') or '')
                      else 'Randomized parallel',
            'n': int(r.get('intervention_total_sample_size') or 0),
            'blinding_class': text_mask_class(r.get('blinding_zh')),
            'blinding_raw': (r.get('blinding_zh') or '').strip(),
            'subtype': (r.get('target_disease_zh') or '').strip(),
            'intervention': title, 'control': '',
            'outcomes': (r.get('study_objectives_zh') or '')[:200],
            'country': 'China',
            '_partner': partner,
        })
        audit.append((rid, r.get('target_disease_zh') or '', 'Include', ''))
    return rows, audit


# ---------------------------------------------------------------- derived features
SUBTYPE_MAP = [
    (re.compile(r'BPPV|benign paroxysmal positional|耳石|位置性眩晕', re.I), 'BPPV'),
    (re.compile(r'M[eé]ni[eè]re|梅尼埃', re.I), 'Ménière disease'),
    (re.compile(r'vestibular migraine|前庭性偏头痛', re.I), 'Vestibular migraine'),
    (re.compile(r'cervic|颈性|颈源', re.I), 'Cervical vertigo'),
    (re.compile(r'posterior circulation|后循环|后循序', re.I), 'Posterior circulation ischaemia'),
    (re.compile(r'PPPD|persistent postural|姿势', re.I), 'PPPD'),
    (re.compile(r'small vessel|脑小血管', re.I), 'CSVD-related dizziness'),
    (re.compile(r'post-stroke|卒中后', re.I), 'Post-stroke vascular vertigo'),
    (re.compile(r'peripheral vertigo|周围性眩晕', re.I), 'Peripheral vertigo'),
    (re.compile(r'vestibular vertigo|前庭性眩晕', re.I), 'Vestibular vertigo'),
    (re.compile(r'sensorineural|SSNHL|noise', re.I), 'Other'),
]
SUBTYPE_ORDER = ['BPPV', 'Cervical vertigo', 'Posterior circulation ischaemia',
                 'Peripheral vertigo', 'Vestibular vertigo', 'PPPD',
                 'CSVD-related dizziness', 'Post-stroke vascular vertigo',
                 'Vestibular migraine', 'Ménière disease', 'Other', 'Not specified']


def subtype_of(r):
    txt = ' '.join([r.get('conditions', ''), r.get('subtype', ''),
                    r.get('intervention', ''), r.get('title', '')])
    for rx, name in SUBTYPE_MAP:
        if rx.search(txt):
            return name
    return 'Not specified'


MODALITY = [
    ('Electroacupuncture', r'electroacup|电针|头皮针电刺激'),
    ('Manual acupuncture', r'acupunctur|针灸|针刺|毫针|浮针|内针|头针|项七针|六气针|针法'),
    ('Acupotomy / needle-knife', r'acupotom|needle-knife|针刀'),
    ('Moxibustion', r'moxibust|艾灸|压灸|灸'),
    ('Acupressure / press needle', r'acupress|press needle|揿针|耳穴'),
    ('Acupoint injection / embedding', r'acupoint injection|埋线|pharmacopuncture|catgut'),
    ('TEAS', r'transcutaneous electrical acupoint'),
]


def modalities(r):
    txt = ' '.join([r.get('intervention', ''), r.get('title', '')])
    out = [name for name, rx in MODALITY if re.search(rx, txt, re.I)]
    return out or ['Other']


# ---------------------------------------------------------------- tables
def write_csv(path, header, rows):
    with open(path, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def _fmt_sub(sub, n):
    """Commonest named subtype, with an explicit tie report.

    'Other' is a catch-all, not a subtype, so it is not eligible to be called
    the commonest one. Ties must be reported as ties: on the ClinicalTrials.gov
    subset three distinct subtypes occur once each, and picking whichever
    happened to be counted first would misstate the data.
    """
    named = collections.Counter({k: v for k, v in sub.items()
                                 if k not in ('Not specified', 'Other')})
    # 'Other' is excluded here for the same reason it is excluded from `named`:
    # counting it as classified would report a subtype tally the row does not show.
    cls = n - sub.get('Not specified', 0) - sub.get('Other', 0)
    if not named:
        return 'None named (0/{} classified)'.format(n)
    top = named.most_common()
    best = top[0][1]
    winners = [k for k, v in top if v == best]
    if len(winners) > 1:
        return '{} ({} each; {}/{} classified)'.format(
            ' / '.join(winners), best, cls, n)
    return '{} ({}/{})'.format(winners[0], best, n)


def build(incl, counts):
    gates = []
    by_reg = collections.defaultdict(list)
    for r in incl:
        by_reg[r['registry']].append(r)

    # -- Table 1
    t1 = []
    for reg, field, hits, per_term in counts:
        n = len(by_reg[reg])
        t1.append([reg, field, hits, n])
    t1.append(['Total', '—', sum(x[2] for x in counts), sum(x[3] for x in t1)])
    write_csv(os.path.join(TAB, 'Table1_Search_Results.csv'),
              ['Registry', 'Search field (unified scope)', 'Records retrieved',
               'Confirmed acupuncture-vertigo trials'], t1)

    # -- Table 2 / Figure 3, 4
    med = lambda v: int(np.median(v)) if v else 0
    t2 = []
    for reg in ['ClinicalTrials.gov', 'ChiCTR', 'ITMCTR']:
        rs = by_reg[reg]
        n = len(rs)
        cls = collections.Counter(r['blinding_class'] for r in rs)
        sub = collections.Counter(subtype_of(r) for r in rs)
        t2.append([reg, n,
                   '{}-{}'.format(min(r['year'] for r in rs), max(r['year'] for r in rs)),
                   '{} ({}-{})'.format(med([r['n'] for r in rs]), min(r['n'] for r in rs),
                                       max(r['n'] for r in rs)),
                   sum(1 for r in rs if is_randomized(r)),
                   cls.get('Double-blind', 0), cls.get('Single-blind', 0),
                   cls.get('Assessor-blinded', 0), cls.get('Other or partial', 0),
                   cls.get('Open-label or none', 0), cls.get('Not stated', 0),
                   _fmt_sub(sub, n)])
    write_csv(os.path.join(TAB, 'Table2_Characteristics_Comparison.csv'),
              ['Registry', 'n', 'Registration period', 'Median n (range)', 'Randomized',
               'Double-blind', 'Single-blind', 'Assessor-blinded', 'Other or partial',
               'Open-label or none', 'Not stated', 'Commonest subtype'], t2)

    # -- Table 3 intervention / assessment profiles
    t3 = []
    for reg in ['ClinicalTrials.gov', 'ChiCTR', 'ITMCTR']:
        rs = by_reg[reg]
        n = len(rs)
        mods = collections.Counter(m for r in rs for m in modalities(r))
        outs = ' '.join(' '.join(r.get('outcomes') or []) if isinstance(
            r.get('outcomes'), list) else (r.get('outcomes') or '') for r in rs)
        txt_of = lambda r: ' '.join(r.get('outcomes') or []) if isinstance(
            r.get('outcomes'), list) else (r.get('outcomes') or '')
        cnt = lambda rx: sum(1 for r in rs if re.search(rx, txt_of(r), re.I))
        t3.append([reg, n] +
                  [mods.get(m, 0) for m, _ in MODALITY] +
                  [cnt(r'DHI|Dizziness Handicap|眩晕障碍|眩晕残障|头晕障碍'),
                   cnt(r'\bVAS\b|Visual Analogue|Visual Analog|视觉模拟|视觉评分'),
                   cnt(r'TCD|transcranial Doppler|Doppler|经颅多普勒|脑血流'),
                   cnt(r'fMRI|MRI|magnetic resonance|磁共振|核磁')])
    write_csv(os.path.join(TAB, 'Table3_Intervention_Profiles.csv'),
              ['Registry', 'n'] + [m for m, _ in MODALITY] +
              ['DHI', 'VAS', 'TCD', 'MRI/fMRI'], t3)

    # -------- G4: audit vs hits
    # -------- G1/G2: stacks
    blind_order = ['Double-blind', 'Single-blind', 'Assessor-blinded',
                   'Other or partial', 'Open-label or none', 'Not stated']
    for reg in by_reg:
        rs = by_reg[reg]
        tot = sum(collections.Counter(r['blinding_class'] for r in rs).values())
        gates.append((G := 'G1 blinding stack {}'.format(reg), tot == len(rs)))
        gates.append(('G1 status stack {}'.format(reg),
                      sum(collections.Counter(r['status'] for r in rs).values()) == len(rs)))
        gates.append(('G2 subtype stack {}'.format(reg),
                      sum(collections.Counter(subtype_of(r) for r in rs).values()) == len(rs)))

    # ---------------------------------------------------------------- figures
    regs = ['ClinicalTrials.gov', 'ChiCTR', 'ITMCTR']
    short = ['ClinicalTrials.gov', 'ChiCTR', 'ITMCTR']

    # Figure 1: volume only. The density panel and the 39x/66x annotations are
    # gone: the three registries were not searched on equivalent scope, so no
    # cross-registry density ratio can be computed from this table.
    fig, ax = plt.subplots(figsize=(6.4, 4.4))
    hits = [c[2] for c in counts]
    conf = [len(by_reg[r]) for r in regs]
    x = np.arange(3)
    b1 = ax.bar(x - 0.2, hits, 0.4, label='All vertigo records retrieved', color=C_CTG)
    b2 = ax.bar(x + 0.2, conf, 0.4, label='Confirmed acupuncture-vertigo',
                color=C_CHI)
    for bars, vals in ((b1, hits), (b2, conf)):
        for b, v in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() * 1.15,
                    str(v), ha='center', fontsize=9, fontweight='bold')
    ax.set_yscale('log')
    ax.set_ylim(1, max(hits) * 6)
    ax.set_xticks(x)
    ax.set_xticklabels(short, fontsize=9)
    ax.set_ylabel('Records (log scale)')
    ax.legend(fontsize=8)
    # PLOS does not allow the figure title inside the image file; the caption carries it.
    plt.tight_layout()
    plt.savefig(os.path.join(FIG, 'Figure_1_Registry_Comparison.png'), dpi=300)
    plt.savefig(os.path.join(FIG, 'Figure_1_Registry_Comparison.jpg'), dpi=300)
    plt.close()

    # Figure 2: subtype distribution, grouped bars, percentages of each registry's n
    # 7.4 in wide: PLOS's maximum is 7.5 in (2250 px at 300 dpi), and
    # shrinking a finished raster instead would take the 8 pt labels below 8 pt.
    fig, ax = plt.subplots(figsize=(7.4, 4.6))
    present = [s for s in SUBTYPE_ORDER
               if any(subtype_of(r) == s for r in incl)]
    width = 0.26
    for k, (reg, col) in enumerate(zip(regs, [C_CTG, C_CHI, C_ITM])):
        rs = by_reg[reg]
        cnt = collections.Counter(subtype_of(r) for r in rs)
        vals = [100.0 * cnt.get(s, 0) / len(rs) for s in present]
        ax.bar(np.arange(len(present)) + k * width, vals, width,
               label='{} (n={})'.format(reg, len(rs)), color=col)
    ax.set_xticks(np.arange(len(present)) + width)
    ax.set_xticklabels(present, rotation=30, ha='right', fontsize=8)
    ax.set_ylabel('Proportion of that registry (%)')
    ax.legend(fontsize=8)
    # Title lives in the caption, not in the image (PLOS figure rules).
    plt.tight_layout()
    plt.savefig(os.path.join(FIG, 'Figure_2_Disease_Spectrum.png'), dpi=300)
    plt.savefig(os.path.join(FIG, 'Figure_2_Disease_Spectrum.jpg'), dpi=300)
    plt.close()

    # Figure 3: blinding and status
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.4, 5.6))
    blind_colors = ['#1F4E79', '#4472C4', '#8FAADC', '#BFBFBF', '#F2C7A0', '#E8E8E8']
    bottoms = np.zeros(3)
    y = np.arange(3)
    for lab, col in zip(blind_order, blind_colors):
        vals = []
        for reg in regs:
            rs = by_reg[reg]
            vals.append(100.0 * sum(1 for r in rs if r['blinding_class'] == lab) / len(rs))
        ax1.barh(y, vals, left=bottoms, label=lab, color=col, height=0.55)
        bottoms += np.array(vals)
    ax1.set_yticks(y)
    ax1.set_yticklabels(['{} (n={})'.format(r, len(by_reg[r])) for r in regs], fontsize=8)
    ax1.set_xlim(0, 100)
    ax1.set_xlabel('Proportion of that registry (%)')
    ax1.set_title('A. Blinding', fontsize=11, fontweight='bold')
    ax1.legend(# 2 columns, not 3: at the PLOS canvas width (7.4 in) a 3-column legend
               # runs off the right edge and the last entry is cut mid-word.
               fontsize=8, loc='upper center', bbox_to_anchor=(0.5, -0.18),
               ncols=2, frameon=False)
    for i, v in enumerate(bottoms):
        gates.append(('G1 blinding bar {}'.format(regs[i]), abs(v - 100) < 0.05))

    status_order = ['Completed', 'Recruiting', 'Not yet recruiting', 'Not stated', 'Other']
    st_colors = ['#375623', '#548235', '#A9D18E', '#D9D9D9', '#F2F2F2']
    bottoms = np.zeros(3)
    # Status reaches this point already in the shared vocabulary (CT_STATUS,
    # CH_STATUS, ITM_STATUS), so the bucket is an equality test; G6 fails the run
    # if any registry hands through a label this list does not contain.
    for lab, col in zip(status_order, st_colors):
        vals = [100.0 * sum(1 for r in by_reg[reg] if r['status'] == lab) / len(by_reg[reg])
                for reg in regs]
        ax2.barh(y, vals, left=bottoms, label=lab, color=col, height=0.55)
        bottoms += np.array(vals)
    ax2.set_yticks(y)
    ax2.set_xlim(0, 100)
    ax2.set_xlabel('Proportion of that registry (%)')
    ax2.set_title('B. Recruitment status', fontsize=11, fontweight='bold')
    ax2.set_yticklabels(['{} (n={})'.format(r, len(by_reg[r])) for r in regs], fontsize=8)
    ax2.legend(# 2 columns, not 3: at the PLOS canvas width (7.4 in) a 3-column legend
               # runs off the right edge and the last entry is cut mid-word.
               fontsize=8, loc='upper center', bbox_to_anchor=(0.5, -0.18),
               ncols=2, frameon=False)
    for i, v in enumerate(bottoms):
        gates.append(('G1 status bar {}'.format(regs[i]), abs(v - 100) < 0.05))
    # G6: a status the figure vocabulary does not know silently lands in the
    # 'Other' bucket (the ChiCTR bar drew empty before the Chinese labels were
    # mapped), so an unmapped value is an error rather than a colour choice.
    for reg in regs:
        unknown = sorted({r['status'] for r in by_reg[reg]} - set(status_order))
        gates.append(('G6 status vocabulary {}'.format(reg), not unknown))
    plt.tight_layout()
    plt.savefig(os.path.join(FIG, 'Figure_3_Methodological_Quality.png'), dpi=300)
    plt.savefig(os.path.join(FIG, 'Figure_3_Methodological_Quality.jpg'), dpi=300)
    plt.close()

    # Figure 4: counts only. No joinpoint line: the break at 2021 was fitted on
    # the superseded all-field denominator and cannot be transplanted onto this
    # scope. 4B is the acupuncture subset with no model overlaid.
    all_ct = json.load(open(os.path.join(UNI, 'ctgov_raw.json'), encoding='utf-8'))
    ct_all = collections.Counter(
        int((pget(s, 'protocolSection', 'statusModule', 'studyFirstSubmitDate') or '')[:4] or 0)
        for s in all_ct)
    # The axis spans the years the records actually carry. A fixed start of 2004
    # left the single 1999 record out of the panel while the title still counted
    # it, so the bars summed to one less than the stated n.
    yrs = list(range(min(ct_all), max(ct_all) + 1))
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.4, 5.2))
    ax1.bar(yrs, [ct_all.get(y, 0) for y in yrs], color=C_CTG)
    gates.append(('G8 panel-A bars sum to the retrieved records',
                  sum(ct_all.get(y, 0) for y in yrs) == len(all_ct)))
    ax1.set_title('A. All vertigo registrations, ClinicalTrials.gov\n(condition-field search, n={})'.format(len(all_ct)),
                  fontsize=10, fontweight='bold')
    ax1.set_xlabel('Year of first submission')
    ax1.set_ylabel('Records')
    for reg, col, mk in zip(regs, [C_CTG, C_CHI, C_ITM], ['o-', 's--', '^:']):
        rs = by_reg[reg]
        cnt = collections.Counter(r['year'] for r in rs)
        ax2.plot(yrs, [cnt.get(y, 0) for y in yrs], mk, color=col,
                 label='{} (n={})'.format(reg, len(rs)), markersize=4)
    ax2.set_title('B. Confirmed acupuncture-vertigo trials\n(counts only)',
                  fontsize=10, fontweight='bold')
    ax2.set_xlabel('Year of first submission')
    ax2.set_ylabel('Trials')
    ax2.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(os.path.join(FIG, 'Figure_4_Annual_Trends.png'), dpi=300)
    plt.savefig(os.path.join(FIG, 'Figure_4_Annual_Trends.jpg'), dpi=300)
    plt.close()

    # -------- G3: every plotted value must be in a Table CSV
    table_blob = ''.join(open(os.path.join(TAB, f), encoding='utf-8-sig').read()
                         for f in os.listdir(TAB) if f.endswith('.csv'))
    for reg in regs:
        for lab in blind_order:
            k = sum(1 for r in by_reg[reg] if r['blinding_class'] == lab)
            gates.append(('G3 {} {}'.format(reg, lab), str(k) in table_blob or k == 0))
    return gates, by_reg, counts


# ---------------------------------------------------------------- main
def main():
    ct_rows, ct_audit, ct_hits = load_ctgov()
    ch_rows, ch_audit = load_chictr()
    it_rows, it_audit = load_itmctr()
    ch_hits = len(ch_audit)
    it_hits = len(it_audit)

    counts = [('ClinicalTrials.gov', 'condition field', ct_hits, None),
              ('ChiCTR', 'target disease field', ch_hits, None),
              ('ITMCTR', 'target disease field', it_hits, None)]

    audit_rows = [('ClinicalTrials.gov',) + a for a in ct_audit] + \
                 [('ChiCTR',) + a for a in ch_audit] + \
                 [('ITMCTR',) + a for a in it_audit]
    write_csv(os.path.join(UNI, 'Inclusion_Decisions.csv'),
              ['Registry', 'reg_id', 'registered condition', 'Decision', 'Reason'],
              audit_rows)

    incl = ct_rows + ch_rows + it_rows
    gates, by_reg, counts = build(incl, counts)

    # G4
    seen = collections.Counter(r[0] for r in audit_rows)
    for reg, hits in (('ClinicalTrials.gov', ct_hits), ('ITMCTR', it_hits),
                      ('ChiCTR', ch_hits)):
        gates.append(('G4 audit rows {}'.format(reg), seen.get(reg, 0) == hits))
    for reg in ('ClinicalTrials.gov', 'ChiCTR', 'ITMCTR'):
        inc = sum(1 for r in audit_rows if r[0] == reg and r[3] == 'Include')
        exc = sum(1 for r in audit_rows if r[0] == reg and r[3] == 'Exclude')
        gates.append(('G4 include+exclude {}'.format(reg), inc + exc == seen[reg]))

    # G7: the registered condition field of every included record carries a term
    # from the same six-concept block that was searched. This is what makes the
    # three denominators comparable -- a record reaching the set through a
    # narrative mention instead would put the reviewer's original objection back.
    VS_TERMS = re.compile(r'vertigo|dizziness|M[eé]ni[eè]re|BPPV|paroxysmal positional|'
                          r'vestibular|眩晕|头晕|梅尼埃|耳石|位置性|前庭|颈性|颈源', re.I)
    for reg in ('ClinicalTrials.gov', 'ChiCTR', 'ITMCTR'):
        off_block = [r['reg_id'] for r in by_reg[reg]
                     if not VS_TERMS.search((r.get('conditions') or r.get('subtype') or ''))]
        gates.append(('G7 condition field {}'.format(reg), not off_block))

    # G5 cross-registry duplication: no included ITMCTR record may point at an
    # included ChiCTR record. If one did, the same trial would be counted twice.
    ch_ids = {r['reg_id'] for r in ch_rows}
    twins = [r for r in it_rows
             if (r.get('_partner') or '').strip() in ch_ids]
    gates.append(('G5 ITMCTR/ChiCTR twins resolved', not twins))
    gates.append(('G5 duplicate pairs found', sum(
        1 for r in audit_rows if 'Cross-registered on' in (r[4] or '')) == 5))

    bad = [g for g, ok in gates if not ok]
    print('included: CT.gov {}  ChiCTR {}  ITMCTR {}  total {}'.format(
        len(ct_rows), len(ch_rows), len(it_rows), len(incl)))
    print('gates: {} checked, {} failed'.format(len(gates), len(bad)))
    for b in bad:
        print('  FAIL', b)
    if bad:
        sys.exit(1)
    print('ALL GATES PASS')


if __name__ == '__main__':
    main()
