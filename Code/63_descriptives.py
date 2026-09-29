#!/usr/bin/env python3
"""Descriptive statistics for the rewritten Results section.

Reuses the loaders in 62_rebuild_tables_figures.py verbatim, so every number
printed here comes from the same screened set that produced Tables 1-3 and
Figures 1-4. Nothing is hard-coded; nothing is derived by hand.

Run: python 63_descriptives.py
"""
import collections, importlib.util, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location(
    'rebuild', os.path.join(HERE, '62_rebuild_tables_figures.py'))
R = importlib.util.module_from_spec(spec)
spec.loader.exec_module(R)

ct, _, ct_hits = R.load_ctgov()
ch, _ = R.load_chictr()
it, _ = R.load_itmctr()
by = {'ClinicalTrials.gov': ct, 'ChiCTR': ch, 'ITMCTR': it}


def pct(k, n):
    return '{}/{} = {:.1f}%'.format(k, n, 100.0 * k / n)


def block(title):
    print('\n' + '=' * 68)
    print(title)
    print('=' * 68)


for reg in ('ClinicalTrials.gov', 'ChiCTR', 'ITMCTR'):
    rows = by[reg]
    n = len(rows)
    block('{}  (n = {})'.format(reg, n))

    yrs = sorted(r['year'] for r in rows)
    print('registration years: {} .. {}'.format(yrs[0], yrs[-1]))
    print('  per year:', dict(sorted(collections.Counter(yrs).items())))

    ns = sorted(r['n'] for r in rows if r['n'])
    if ns:
        mid = ns[len(ns) // 2] if len(ns) % 2 else (ns[len(ns) // 2 - 1] + ns[len(ns) // 2]) / 2
        print('planned enrolment: n={}  median={}  range={}-{}'.format(
            len(ns), mid, ns[0], ns[-1]))

    print('design:', dict(collections.Counter(r.get('design') or 'Not stated' for r in rows)))
    print('status:', dict(collections.Counter(r['status'] for r in rows)))

    bl = collections.Counter(r['blinding_class'] for r in rows)
    print('blinding class:')
    for k in ['Double-blind', 'Single-blind', 'Assessor-blinded',
              'Other or partial', 'Open-label or none', 'Not stated']:
        print('   {:<20} {}'.format(k, pct(bl.get(k, 0), n)))

    st = collections.Counter(R.subtype_of(r) for r in rows)
    print('subtype:')
    for k in R.SUBTYPE_ORDER:
        if st.get(k):
            print('   {:<32} {}'.format(k, pct(st[k], n)))

    md = collections.Counter()
    for r in rows:
        for m in R.modalities(r):
            md[m] += 1
    print('modalities:', {k: '{} ({})'.format(v, pct(v, n)) for k, v in md.most_common()})

    print('country:', dict(collections.Counter(r.get('country') or 'Not stated' for r in rows)))

    if reg == 'ClinicalTrials.gov':
        conds = collections.Counter()
        for r in rows:
            for c in (r['conditions'] or '').split(';'):
                if c.strip():
                    conds[c.strip()] += 1
        print('registered conditions:', dict(conds))
        print('raw masking/whoMasked pairs:')
        for r in rows:
            print('   {}  {} / {}  -> {}'.format(
                r['reg_id'], r['masking'], r['who'], r['blinding_class']))
    else:
        print('raw blinding strings:')
        for r in rows:
            print('   {}  "{}"  -> {}'.format(r['reg_id'], r['blinding_raw'],
                                              r['blinding_class']))

block('TOTALS')
print('hits  CT.gov {}  ChiCTR {}  ITMCTR {}'.format(
    ct_hits, len(R.load_chictr()[1]), len(R.load_itmctr()[1])))
print('included  CT.gov {}  ChiCTR {}  ITMCTR {}  total {}'.format(
    len(ct), len(ch), len(it), len(ct) + len(ch) + len(it)))
