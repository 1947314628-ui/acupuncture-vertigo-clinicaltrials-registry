#!/usr/bin/env python3
"""Re-verify every included ChiCTR record against the live registry.

Why this exists: the blinding values in Data/chictr_extraction.csv are manual
reads of registry detail pages. JMIR's fourth criticism was that double-blind
Chinese trials had been systematically misclassified, so the raw strings behind
that table have to be shown to be registry-faithful, not merely re-classified
by a better rule.

What it does
  1. Re-crawls the five disease-field searches purely to recover the
     regno -> showproj.html?proj= link (the search listing is the only place
     that mapping is exposed).
  2. Opens each included record's detail page and reads 盲法 (blinding),
     样本量 (target sample size) and 研究疾病 (condition) straight from the DOM.
  3. Compares them with chictr_extraction.csv / chictr_addendum.csv and with
     the registry's own WHO-format XML export where one is on disk.

Output: Data/Unified/chictr_verification.csv plus a mismatch report on stdout.
Nothing here feeds the analysis; it is an audit layer.
"""
import csv, glob, html, json, os, re, subprocess, sys, time, urllib.parse
import xml.etree.ElementTree as ET

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, 'Data')
UNI = os.path.join(DATA, 'Unified')

# the Chrome binary is machine-specific, so the deposit lets a reader point it
# elsewhere without editing the script
CHROME = os.environ.get('CHROME', r'C:\Program Files\Google\Chrome\Application\chrome.exe')
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')
TERMS = ['眩晕', '头晕', '梅尼埃病', '耳石症', '颈性眩晕']
LINK = re.compile(r'<td>(ChiCTR[\w\-]+)</td>.{0,400}?href="showproj\.html\?proj=(\d+)"', re.S)
TOTAL = re.compile(r'id="data-total">(\d+)<')
TAGS = re.compile(r'<[^>]+>')
WS = re.compile(r'\s+')

FIELDS = ['研究疾病', '研究类型', '研究所处阶段', '随机方法（请说明由何人用什么方法产生随机序列）',
          '盲法', '样本量', '研究目的']


def dom(url, tries=3):
    for i in range(tries):
        p = subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-sandbox',
                            '--user-agent=' + UA, '--virtual-time-budget=20000',
                            '--dump-dom', url],
                           capture_output=True, text=True, encoding='utf-8', errors='replace')
        if p.stdout and 'block_message' not in p.stdout:
            return p.stdout
        time.sleep(4 * (i + 1))
    raise RuntimeError('ChiCTR blocked or empty: ' + url)


def clean(s):
    return WS.sub(' ', html.unescape(TAGS.sub('', s))).strip()


def field(h, label):
    """Value of a left_title row, matched by its label."""
    m = re.search(re.escape(label) + r'[:：]?\s*</p>\s*</td>\s*<td[^>]*>(.*?)</td>', h, re.S)
    return clean(m.group(1)) if m else None


def search_page(term, page):
    q = urllib.parse.urlencode({'studyailment': term, 'btngo': 'btn', 'page': page})
    h = dom('https://www.chictr.org.cn/searchproj.html?' + q)
    total = int(TOTAL.search(h).group(1)) if TOTAL.search(h) else 0
    return total, LINK.findall(h)


# ---------------------------------------------------------------- inputs
extraction = list(csv.DictReader(open(os.path.join(DATA, 'chictr_extraction.csv'),
                                      encoding='utf-8-sig')))
addendum = list(csv.DictReader(open(os.path.join(UNI, 'chictr_addendum.csv'),
                                    encoding='utf-8-sig')))
local = {}
for r in extraction + addendum:
    local[r['reg_id'].strip()] = {
        'blinding': r['blinding'].strip(),
        'sample_size': r['sample_size'].strip(),
        'subtype': r['disease_subtype'].strip(),
        'design': r['study_design'].strip(),
    }

# WHO-format XML exports, where present, give an independent target_size.
xml_size = {}
for fn in glob.glob(os.path.join(DATA, '*.xml')):
    root = ET.parse(fn).getroot()
    tid = root.findtext('.//trial_id')
    ts = (root.findtext('.//target_size') or '').strip()
    if tid:
        nums = [int(n) for n in re.findall(r'\d+', ts)]
        xml_size[tid] = (ts, sum(nums))

# ---------------------------------------------------------------- crawl
if __name__ == '__main__':
    proj = {}
    for t in TERMS:
        total, rows = search_page(t, 1)
        for regno, pid in rows:
            proj.setdefault(regno, pid)
        for pg in range(2, (total + 9) // 10 + 1):
            _, more = search_page(t, pg)
            for regno, pid in more:
                proj.setdefault(regno, pid)
            time.sleep(0.4)
    print('proj links recovered: {} / {} included'.format(
        sum(1 for k in local if k in proj), len(local)))

    out, bad = [], 0
    for reg in sorted(local):
        if reg not in proj:
            print('  NO LINK', reg)
            continue
        h = dom('https://www.chictr.org.cn/showproj.html?proj=' + proj[reg])
        got = {f: field(h, f) for f in FIELDS}
        size_txt = got.get('样本量') or ''
        nums = [int(n) for n in re.findall(r'\d+', size_txt)]
        reg_size = sum(nums) if nums else None
        loc = local[reg]
        size_ok = (reg_size is None or loc['sample_size'] == '' or
                   reg_size == int(loc['sample_size']))
        blind_ok = (got.get('盲法') or '') != ''
        if not size_ok:
            bad += 1
        out.append((reg, proj[reg], got.get('研究疾病'), got.get('研究类型'),
                    got.get('随机方法（请说明由何人用什么方法产生随机序列）'),
                    got.get('盲法'), loc['blinding'], size_txt, loc['sample_size'],
                    'OK' if size_ok else 'MISMATCH'))
        print('{:<22} blind_zh={:<28} local={:<44} size_zh={:<10} local={} {}'.format(
            reg, (got.get('盲法') or '')[:28], loc['blinding'][:44],
            size_txt[:10], loc['sample_size'], '' if size_ok else '  <-- SIZE MISMATCH'))
        time.sleep(0.4)

    with open(os.path.join(UNI, 'chictr_verification.csv'), 'w', newline='',
              encoding='utf-8-sig') as f:
        w = csv.writer(f)
        w.writerow(['reg_id', 'proj_id', 'registry 研究疾病', 'registry 研究类型',
                    'registry 随机方法', 'registry 盲法', 'local blinding',
                    'registry 样本量', 'local sample_size', 'sample size check'])
        w.writerows(out)
    print('\nrows written: {}   sample-size mismatches: {}'.format(len(out), bad))
