#!/usr/bin/env python3
"""ChiCTR: rule-derived inclusion set + registry-read fields (JMIR revision).

Two defects this closes, both of the same kind.

1. The ChiCTR numerator came from a hand-kept extraction list. Re-screening the
   170 retrieved records found an acupuncture trial the list had missed
   (ChiCTR2400080734, vestibular migraine) -- the same class of error the
   reviewers rejected the paper for. The set is now derived from the retrieved
   records by the rule below, and every retrieved record carries a decision.

2. Every field of every retrieved record is read back from the registry page
   (intervention, blinding, randomisation, sample size, ailment, outcomes), so no
   number in the manuscript rests on a hand transcription.

Screening rule -- applied to fields the registry itself provides:
  include  the registered intervention names an acupuncture modality (INTRV_RE)
           and the study is interventional (INTERVENTIONAL study type)
  exclude  otherwise, with the reason recorded

Screening runs on 干预措施 (the registered intervention field) as well as the
title, so a trial whose title avoids the word acupuncture is still found. Bare
'针' is deliberately NOT an acupuncture term: it matches 针对 ("targeting"),
which is how an observational anxiety trial entered an earlier candidate set.

Run order: 61_ (search) -> 66_ (this) -> 60_ -> 62_ -> 65_
Outputs: Data/Unified/chictr_projmap.json, chictr_pages/<proj>.json,
         chictr_fields.csv, chictr_screen.csv
"""
import concurrent.futures as cf
import html as _html
import json, os, re, subprocess, sys, time, urllib.parse

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UNI = os.path.join(BASE, 'Data', 'Unified')
PAGES = os.path.join(UNI, 'chictr_pages')
os.makedirs(PAGES, exist_ok=True)

# the Chrome binary is machine-specific, so the deposit lets a reader point it
# elsewhere without editing the script
CHROME = os.environ.get('CHROME', r'C:\Program Files\Google\Chrome\Application\chrome.exe')
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')
TERMS = ['眩晕', '头晕', '梅尼埃病', '耳石症', '前庭性偏头痛', '颈性眩晕']

# Acupuncture-family modality, one entry per registered modality. No bare 针 --
# it matches 针对 ("targeting"), which is how an observational anxiety trial
# entered an earlier candidate set -- and no bare 穴位, which matches 穴位推拿
# (acupoint tuina), a manual-therapy modality. 穴位 counts only in the
# acupoint-stimulation forms spelled out below.
INTRV_RE = re.compile(
    r'针刺|针灸|电针|毫针|温针|针刀|揿针|皮内针|火针|头针|头皮针|腹针|浮针|脐针|'
    r'针法|岐黄针|腕踝针|梅花针|平衡针|靳三针|内针|埋线|艾灸|艾条灸|艾炷灸|隔物灸|'
    r'灸法|灸疗|雷火灸|热敏灸|耳穴|穴位埋线|穴位注射|穴位贴敷|穴位按压|穴位电刺激|'
    r'经皮穴位电刺激|transcutaneous electrical acupoint|acupunctur|electroacup|'
    r'acupotom|acupress|moxibust|acupoint injection|catgut|pharmacopuncture|teas', re.I)
# Registered interventions that are not needling/acupoint therapies: manual
# therapy and repositioning. A record is excluded when its intervention names one
# of these and names no needling modality -- ChiCTR-ION-16009815 is "一指禅穴位
# 推拿" (acupoint tuina). A manual modality alongside needling is a co-intervention
# and does not by itself exclude: ChiCTR2400086666 pairs 针灸 with 扳法.
NOT_ACU_RE = re.compile(
    r'推拿|按摩|手法复位|扳法|整脊|脊椎矫正|牵引|tuina|massage|manipulation|'
    r'chiropract|repositioning|traction', re.I)
# Needling and needling-adjacent modalities. Used only to decide whether a manual
# modality is the whole intervention or a co-intervention.
NEEDLE_RE = re.compile(
    r'针刺|针灸|电针|毫针|温针|针刀|揿针|皮内针|火针|头针|头皮针|腹针|浮针|脐针|'
    r'针法|岐黄针|腕踝针|梅花针|平衡针|靳三针|内针|埋线|needl|acupunct|electroacup|'
    r'acupotom|catgut|pharmacopuncture', re.I)
# Study types that register an intervention. The rest (观察性研究, 诊断试验, ...)
# do not test a treatment and are outside the review question.
INTERVENTIONAL = re.compile(r'干预性研究|治疗研究|预防性研究')

ROWSPLIT = re.compile(r'<tr[^>]*>(.*?)</tr>', re.S)
REGNO = re.compile(r'ChiCTR[\w\-]+')
PROJ = re.compile(r'showproj\.html\?proj=(\d+)')
TOTAL = re.compile(r'id="data-total">(\d+)<')


def txt(s):
    return re.sub(r'\s+', ' ', _html.unescape(re.sub(r'<[^>]+>', ' ', s))).strip()


def dom(url, tries=4):
    for i in range(tries):
        p = subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-sandbox',
                            '--user-agent=' + UA, '--virtual-time-budget=20000',
                            '--dump-dom', url],
                           capture_output=True, text=True, encoding='utf-8', errors='replace')
        if p.stdout and 'block_message' not in p.stdout:
            return p.stdout
        time.sleep(5 * (i + 1))
    raise RuntimeError('ChiCTR blocked or empty: ' + url)


# ------------------------------------------------------------------ regno -> proj
def search_page(term, page):
    q = urllib.parse.urlencode({'studyailment': term, 'btngo': 'btn', 'page': page})
    return dom('https://www.chictr.org.cn/searchproj.html?' + q)


def build_projmap():
    path = os.path.join(UNI, 'chictr_projmap.json')
    if os.path.exists(path):
        return json.load(open(path, encoding='utf-8'))
    m = {}
    for t in TERMS:
        first = search_page(t, 1)
        total = int(TOTAL.search(first).group(1)) if TOTAL.search(first) else 0
        pages = [(t, 1, first)]
        for pg in range(2, (total + 9) // 10 + 1):
            pages.append((t, pg, search_page(t, pg)))
        for term, pg, doc in pages:
            for row in ROWSPLIT.findall(doc):
                r, p = REGNO.search(row), PROJ.search(row)
                if r and p:
                    m[r.group(0)] = p.group(1)
        print('  projmap: {} -> {} ids'.format(t, len(m)), flush=True)
    json.dump(m, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    return m


# ------------------------------------------------------------------ detail page
ANCHOR = re.compile(r'<td[^>]*class="left_title"[^>]*>\s*<p class="cn">([^<]*)</p>')


def parse_detail(doc):
    """label -> Chinese value, from a ChiCTR detail page.

    Every field label is a left_title cell holding a <p class="cn"> label and a
    <p class="en"> translation; its value is whatever follows, up to the next
    label. Splitting on the label cells (rather than on <tr>) keeps the nested
    tables that hold the intervention and outcome fields intact — splitting on
    rows truncates them at the first nested </tr>.

    Sample size has no left_title cell of its own (it is a plain td next to the
    recruitment status), so it is read from that field's span.
    """
    hits = list(ANCHOR.finditer(doc))
    out, raws = {}, {}
    for i, m in enumerate(hits):
        lab = m.group(1).strip().rstrip('：:')
        span = doc[m.end():hits[i + 1].start() if i + 1 < len(hits) else len(doc)]
        span = re.sub(r'<p class="en">.*?</p>', ' ', span, flags=re.S)   # English column
        cn = ' '.join(txt(v) for v in re.findall(r'<p class="cn">(.*?)</p>', span, re.S))
        val = txt(cn) if cn else txt(span)
        if lab and lab not in out:
            out[lab], raws[lab] = val, span
    # The record form states the size of each arm, not the trial total, so the
    # total is the sum of the registered arm sizes: the value cell follows the
    # 样本量 label cell inside the intervention table.
    arms = [int(v) for v in re.findall(
        r'样本量：</p>\s*</td>\s*<td[^>]*>\s*([0-9]+)', raws.get('干预措施', ''))]
    out['样本量'] = str(sum(arms)) if arms else ''
    out['样本量_分组'] = '; '.join(str(a) for a in arms)
    out['征募研究对象情况'] = re.sub(
        r'\s*样本量：.*$', '', out.get('征募研究对象情况', '')).strip()
    return out


def fetch_detail(proj):
    """Cache the raw registry page, not the parse.

    Raw pages are kept so that a parser fix does not mean re-crawling, and so the
    submitted audit can point at the exact page each value came from.
    """
    cache = os.path.join(PAGES, proj + '.html')
    if os.path.exists(cache):
        return proj
    open(cache, 'w', encoding='utf-8').write(
        dom('https://www.chictr.org.cn/showproj.html?proj=' + proj))
    return proj


def read_detail(proj):
    path = os.path.join(PAGES, proj + '.html')
    if not os.path.exists(path):
        return {}
    return parse_detail(open(path, encoding='utf-8').read())


def year_of(s):
    m = re.search(r'(20\d\d)', s or '')
    return int(m.group(1)) if m else 0


if __name__ == '__main__':
    raw = json.load(open(os.path.join(UNI, 'chictr_raw.json'), encoding='utf-8'))
    print('retrieved records: {}'.format(len(raw)), flush=True)
    pmap = build_projmap()
    print('proj ids mapped: {}'.format(len(pmap)), flush=True)
    missing = [r['regno'] for r in raw if r['regno'] not in pmap]
    if missing:
        print('WARNING no detail page located for: {}'.format(missing), flush=True)

    # ---- fetch every retrieved record's detail page (resumable, cached)
    todo = [pmap[r['regno']] for r in raw if r['regno'] in pmap]
    print('detail pages to fetch: {} (cached: {})'.format(
        len(todo), len(os.listdir(PAGES))), flush=True)
    done = 0
    with cf.ThreadPoolExecutor(max_workers=3) as ex:
        for _ in ex.map(fetch_detail, todo):
            done += 1
            if done % 20 == 0:
                print('  fetched {}/{}'.format(done, len(todo)), flush=True)

    # ---- screen, and write the decision for every retrieved record
    screen, fields, included = [], [], []
    for r in raw:
        rid, title = r['regno'], r['title']
        det = read_detail(pmap[rid]) if rid in pmap else {}
        intrv = det.get('干预措施', '')
        text = title + ' ' + intrv
        acu = INTRV_RE.search(text)
        inter = INTERVENTIONAL.search(r['study_type'])
        non_acu = NOT_ACU_RE.search(text)
        needle = NEEDLE_RE.search(text)
        if acu and inter and not (non_acu and not needle):
            decision, reason = 'Include', ''
        elif acu and inter:
            decision = 'Exclude'
            reason = ('Registered intervention is a manual-therapy modality ({}), not a '
                      'needling or acupoint therapy'.format(non_acu.group(0)))
        elif not inter:
            decision = 'Exclude'
            reason = 'Registered study type is {}, not an interventional design'.format(
                r['study_type'])
        else:
            decision = 'Exclude'
            reason = ('Registered intervention names no acupuncture-family modality '
                      '(no term in the acupuncture word list matches the title or the '
                      'registered intervention field)')
        screen.append(['ChiCTR', rid, det.get('研究疾病', title), decision, reason])
        if decision != 'Include':
            continue
        included.append(rid)
        fields.append({
            'reg_id': rid, 'proj': pmap.get(rid, ''), 'title': title,
            'registration_date': det.get('注册时间', ''), 'year': year_of(det.get('注册时间', '')),
            'status': det.get('征募研究对象情况', ''),
            'study_type': r['study_type'], 'study_design': det.get('研究设计', ''),
            'randomisation': det.get('随机方法（请说明由何人用什么方法产生随机序列）', ''),
            'blinding': det.get('盲法', ''), 'sample_size': det.get('样本量', ''),
            'disease': det.get('研究疾病', ''), 'intervention': intrv,
            'outcomes': det.get('测量指标', ''), 'purpose': det.get('研究目的', ''),
            'partner': det.get('在二级注册机构或其它机构的注册号', ''),
            'site': det.get('研究实施负责（组长）单位', ''),
        })

    json.dump(fields, open(os.path.join(UNI, 'chictr_fields.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    import csv
    with open(os.path.join(UNI, 'chictr_screen.csv'), 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        w.writerow(['Registry', 'reg_id', 'registered condition', 'Decision', 'Reason'])
        w.writerows(screen)
    with open(os.path.join(UNI, 'chictr_included.csv'), 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=list(fields[0].keys()))
        w.writeheader()
        w.writerows(fields)

    print('\nincluded {} of {}'.format(len(included), len(raw)))
    for d in fields:
        print('  {} | {} | n={} | {} | {}'.format(
            d['reg_id'], d['year'], d['sample_size'], d['disease'][:20], d['blinding'][:48]))
    print('\n0 rows written with an unread detail page: {}'.format(
        sum(1 for d in fields if not d['blinding'] and not d['sample_size'])))
