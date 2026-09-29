#!/usr/bin/env python3
"""ChiCTR disease-field search via headless Chrome (JMIR revision, S8).

ChiCTR is behind an Aliyun WAF: plain HTTP gets a 405 block page. Headless
Chrome works *only* when a real (non-HeadlessChrome) User-Agent is supplied.
Do not drop the --user-agent flag.

Search field is `studyailment` (目标疾病). Same six-term Chinese block as ITMCTR,
which is the concept-for-concept counterpart of the six English terms used on
ClinicalTrials.gov.

Output: Data/Unified/chictr_raw.json  +  counts appended to Search_Log_Unified.md
"""
import json, os, re, subprocess, sys, time, urllib.parse

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, 'Data', 'Unified')
os.makedirs(OUT, exist_ok=True)

# the Chrome binary is machine-specific, so the deposit lets a reader point it
# elsewhere without editing the script
CHROME = os.environ.get('CHROME', r'C:\Program Files\Google\Chrome\Application\chrome.exe')
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')
TERMS = ['眩晕', '头晕', '梅尼埃病', '耳石症', '前庭性偏头痛', '颈性眩晕']

ROW = re.compile(r'<td>(ChiCTR[\w\-]+)</td>\s*<td>.*?title="([^"]*)".*?<p>([^<]*)</p>.*?'
                 r'<td>([^<]*)</td>\s*<td>([\d/]+)</td>', re.S)
TOTAL = re.compile(r'id="data-total">(\d+)<')


def dom(url, tries=3):
    for i in range(tries):
        p = subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-sandbox',
                            '--user-agent=' + UA, '--virtual-time-budget=20000',
                            '--dump-dom', url],
                           capture_output=True, text=True, encoding='utf-8', errors='replace')
        if 'block_message' not in p.stdout and p.stdout:
            return p.stdout
        time.sleep(4 * (i + 1))
    raise RuntimeError('ChiCTR blocked or empty after retries: ' + url)


def search(term, page=1):
    q = urllib.parse.urlencode({'studyailment': term, 'btngo': 'btn', 'page': page})
    html = dom('https://www.chictr.org.cn/searchproj.html?' + q)
    total = int(TOTAL.search(html).group(1)) if TOTAL.search(html) else 0
    rows = [{'regno': m[0], 'title': m[1], 'institution': m[2],
             'study_type': m[3], 'date': m[4], 'matched_term': term}
            for m in ROW.findall(html)]
    return total, rows


if __name__ == '__main__':
    counts, seen, all_rows = {}, {}, {}
    for t in TERMS:
        total, rows = search(t)
        counts[t] = total
        all_rows[t] = rows
        print('{} => {} (page1 rows: {})'.format(t, total, len(rows)), flush=True)
        for r in rows:
            seen.setdefault(r['regno'], r)
        for pg in range(2, (total + 9) // 10 + 1):
            _, more = search(t, pg)
            for r in more:
                seen.setdefault(r['regno'], r)
            time.sleep(0.5)
        print('   pages done, running unique = {}'.format(len(seen)), flush=True)

    json.dump(list(seen.values()), open(os.path.join(OUT, 'chictr_raw.json'), 'w',
              encoding='utf-8'), ensure_ascii=False, indent=1)
    # Per-term counts are written to their own file so that 60_search_registries.py
    # can assemble the whole search log in one pass. Run order: 61 first, then 60.
    json.dump({'per_term': counts, 'unique': len(seen)},
              open(os.path.join(OUT, 'chictr_counts.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('unique =', len(seen))
