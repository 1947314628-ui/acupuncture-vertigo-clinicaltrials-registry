#!/usr/bin/env python3
"""Unified three-registry search (JMIR revision, Step 2 / S8).

One protocol, one word list, one field per registry:
  ClinicalTrials.gov -> condition field only (query.cond)
  ITMCTR             -> target_disease field only
  ChiCTR             -> studyailment field only (needs headless browser, see 61_)

Outputs (all under Data/Unified/):
  ctgov_raw.json            full records, condition-field hits
  itmctr_search_log.csv     term -> totalCount
  Search_Log_Unified.md     human-readable, one runnable command per denominator

No derived denominators. Every number in the log is a count returned by the API.
"""
import csv, datetime, json, os, sys, time, urllib.parse, urllib.request

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, 'Data', 'Unified')
os.makedirs(OUT, exist_ok=True)

# Six vertigo concepts, expressed in both languages, one term per concept per
# language. The blocks must stay concept-for-concept parallel: an earlier run
# dropped vestibular migraine from the Chinese side, which silently removed an
# ITMCTR acupuncture trial for vestibular migraine and made "vestibular migraine
# is registered only on ClinicalTrials.gov" an artefact of the word list.
VERTIGO_EN = ['vertigo', 'dizziness', 'Meniere', 'BPPV', 'vestibular migraine',
              'cervical vertigo']
VERTIGO_ZH = ['眩晕', '头晕', '梅尼埃病', '耳石症', '前庭性偏头痛', '颈性眩晕']
ACU_TERMS = ['acupuncture', 'electroacupuncture', 'acupoint', 'moxibustion',
             'acupressure', 'auricular acupuncture', 'scalp acupuncture',
             'transcutaneous electrical acupoint stimulation', 'acupotomy',
             'catgut embedding', 'dry needling', 'pharmacopuncture',
             'needle', 'teas']

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}


def get(url, timeout=90, tries=3):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
                return json.load(r)
        except Exception as e:
            if i == tries - 1:
                raise
            time.sleep(3 * (i + 1))


# ---------------------------------------------------------------- ClinicalTrials.gov
def ctgov_cond(expr):
    """totalCount for a condition-field query. OR expressions must NOT be quoted."""
    q = urllib.parse.urlencode({'query.cond': expr, 'countTotal': 'true',
                                'pageSize': '1', 'fields': 'NCTId'})
    d = get('https://clinicaltrials.gov/api/v2/studies?' + q)
    return d.get('totalCount')


def ctgov_fetch(expr):
    """All records for a condition-field query, with the fields we analyse."""
    fields = ','.join([
        'NCTId', 'BriefTitle', 'OfficialTitle', 'OverallStatus', 'StudyType', 'Phase',
        'EnrollmentCount', 'Condition', 'InterventionName', 'InterventionType',
        'LeadSponsorName', 'StartDate', 'StudyFirstSubmitDate', 'PrimaryOutcomeMeasure',
        'DesignAllocation', 'DesignPrimaryPurpose', 'DesignMaskingInfo',
        'DesignWhoMasked', 'ArmGroupLabel', 'LocationCountry',
    ])
    out, token = [], None
    while True:
        p = {'query.cond': expr, 'pageSize': '1000', 'fields': fields}
        if token:
            p['pageToken'] = token
        d = get('https://clinicaltrials.gov/api/v2/studies?' + urllib.parse.urlencode(p))
        out.extend(d.get('studies', []))
        token = d.get('nextPageToken')
        if not token:
            break
    return out


def run_ctgov():
    per_term = {t: ctgov_cond(t) for t in VERTIGO_EN}
    expr = ' OR '.join(VERTIGO_EN)
    total = ctgov_cond(expr)
    studies = ctgov_fetch(expr)
    json.dump(studies, open(os.path.join(OUT, 'ctgov_raw.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    return per_term, expr, total, len(studies)


# ---------------------------------------------------------------- ITMCTR
def itmctr_total(term):
    q = urllib.parse.urlencode({
        '$pageIndex': '1', '$pageSize': '1',
        '$sortBy': 'send_number_time', '$orderBy': 'desc',
        'formCode': 'PROJECT', 'dynamicQueries[target_disease]': term,
    })
    d = get('https://itmctr.ccebtcm.org.cn/itmctr/Project/trialsearch?' + q)
    return d['data']['totals']


def itmctr_fetch(term, size=500):
    q = urllib.parse.urlencode({
        '$pageIndex': '1', '$pageSize': str(size),
        '$sortBy': 'send_number_time', '$orderBy': 'desc',
        'formCode': 'PROJECT', 'dynamicQueries[target_disease]': term,
    })
    d = get('https://itmctr.ccebtcm.org.cn/itmctr/Project/trialsearch?' + q)
    return d['data']['rows']


def run_itmctr():
    per_term = {t: itmctr_total(t) for t in VERTIGO_ZH}
    rows, seen = [], set()
    for t in VERTIGO_ZH:
        for r in itmctr_fetch(t):
            rid = r.get('registration_number')
            if rid and rid not in seen:
                seen.add(rid)
                r['_matched_term'] = t
                rows.append(r)
    json.dump(rows, open(os.path.join(OUT, 'itmctr_raw.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    return per_term, len(rows)


if __name__ == '__main__':
    log = ['# Unified search log', '',
           'Protocol: identical disease-field scope on all three registries, identical word list.',
           'Six vertigo concepts, one term per concept per language.',
           'Retrieval date: {}.'.format(datetime.date.today().isoformat()),
           '', '## ClinicalTrials.gov (condition field only)', '',
           '`query.cond` — run: `python 60_search_registries.py`', '',
           '| term | totalCount |', '|---|---|']
    ct_per, ct_expr, ct_total, ct_n = run_ctgov()
    log += ['| {} | {} |'.format(t, n) for t, n in ct_per.items()]
    log += ['| **OR-combined** | **{}** |'.format(ct_total), '',
            'OR expression used (unquoted — quoting returns 0):', '',
            '```', ct_expr, '```', '',
            'Records downloaded: {}'.format(ct_n), '',
            '## ITMCTR (target_disease field only)', '',
            '`dynamicQueries[target_disease]` — run: `python 60_search_registries.py`', '',
            '| term | totalCount |', '|---|---|']
    it_per, it_n = run_itmctr()
    log += ['| {} | {} |'.format(t, n) for t, n in it_per.items()]
    log += ['', 'Unique records after cross-term dedup: {}'.format(it_n), '',
            '## ChiCTR (studyailment field only)', '',
            'ChiCTR sits behind an Aliyun WAF; the counts below were obtained with a',
            'headless browser, `61_chictr_search.py`, which must be run before this',
            'script so that its counts are on disk.', '',
            '| term | totalCount |', '|---|---|']
    ch_log = os.path.join(OUT, 'chictr_counts.json')
    if os.path.exists(ch_log):
        ch = json.load(open(ch_log, encoding='utf-8'))
        log += ['| {} | {} |'.format(t, n) for t, n in ch['per_term'].items()]
        log += ['', 'Unique records after cross-term dedup: {}'.format(ch['unique'])]
    else:
        sys.exit('run 61_chictr_search.py first: Data/Unified/chictr_counts.json missing')
    open(os.path.join(OUT, 'Search_Log_Unified.md'), 'w', encoding='utf-8').write('\n'.join(log))
    print('\n'.join(log))
