# Unified search log

Protocol: identical disease-field scope on all three registries, identical word list.
Six vertigo concepts, one term per concept per language.
Retrieval date: 2026-09-29.

## ClinicalTrials.gov (condition field only)

`query.cond` — run: `python 60_search_registries.py`

| term | totalCount |
|---|---|
| vertigo | 436 |
| dizziness | 436 |
| Meniere | 76 |
| BPPV | 88 |
| vestibular migraine | 50 |
| cervical vertigo | 32 |
| **OR-combined** | **499** |

OR expression used (unquoted — quoting returns 0):

```
vertigo OR dizziness OR Meniere OR BPPV OR vestibular migraine OR cervical vertigo
```

Records downloaded: 499

## ITMCTR (target_disease field only)

`dynamicQueries[target_disease]` — run: `python 60_search_registries.py`

| term | totalCount |
|---|---|
| 眩晕 | 31 |
| 头晕 | 6 |
| 梅尼埃病 | 0 |
| 耳石症 | 0 |
| 前庭性偏头痛 | 1 |
| 颈性眩晕 | 5 |

Unique records after cross-term dedup: 36

## ChiCTR (studyailment field only)

ChiCTR sits behind an Aliyun WAF; the counts below were obtained with a
headless browser, `61_chictr_search.py`, which must be run before this
script so that its counts are on disk.

| term | totalCount |
|---|---|
| 眩晕 | 102 |
| 头晕 | 40 |
| 梅尼埃病 | 33 |
| 耳石症 | 1 |
| 前庭性偏头痛 | 12 |
| 颈性眩晕 | 10 |

Unique records after cross-term dedup: 170