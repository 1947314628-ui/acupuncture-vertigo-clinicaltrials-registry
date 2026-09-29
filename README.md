# acupuncture-vertigo-clinicaltrials-registry

Data, code and manuscript for the study "Acupuncture clinical trial registration for
vertigo: a descriptive multi-registry comparison of ClinicalTrials.gov, ChiCTR and
ITMCTR (2015-2026)".

Licence: CC BY 4.0. Cite the concept DOI 10.5281/zenodo.21110650, which resolves to
the most recent version; every version keeps its own DOI.

## This version (v2.0) replaces v1.0

v1.0 (tag `v1.0`, 10.5281/zenodo.21110651) searched the three registries on
non-equivalent scope: ClinicalTrials.gov on all fields, the two Chinese registries on
the target-disease field only. The retrieved totals were therefore not comparable,
and no honest ratio could be taken from them. v2.0 was rebuilt:

* **One scope on all three registries.** Each is searched on its disease or condition
  field (ClinicalTrials.gov `query.cond`; ChiCTR `studyailment`; ITMCTR
  `target_disease`) with the same six vertigo concepts in the language of record:
  vertigo, dizziness, Meniere, BPPV, vestibular migraine, cervical vertigo / 眩晕,
  头晕, 梅尼埃病, 耳石症, 前庭性偏头痛, 颈性眩晕. Search date: 29 September 2026.
* **No cross-registry density ratio.** The retrieved totals are not equivalent
  denominators, so the deposit reports counts and nothing derived from comparing them.
* **A decision for every retrieved record.** All 705 retrieved records carry an
  include/exclude decision and the reason for it (`Data/Unified/Inclusion_Decisions.csv`).
* **Registry-read fields.** Every field of every included ChiCTR record is read back
  from the registry page rather than transcribed by hand
  (`Data/Unified/chictr_included.csv`; the pages they were read from are retained in
  `Data/Unified/chictr_pages.zip`).
* **Stated blinding rule.** Double-blind means participants *and* at least one of
  investigators / care providers / outcome assessors; single-blind means participants
  only. The rule is applied to the registry text in both languages, and the raw
  strings are retained in `Data/Unified/chictr_included.csv`.
* **No model over a subset.** The joinpoint model that v1.0 drew over the
  acupuncture subset had been fitted to a larger, differently defined set; Figure 4
  reports counts only.

## Results of the search

| Registry | Search field | Records retrieved | Confirmed acupuncture-vertigo trials |
|---|---|---|---|
| ClinicalTrials.gov | condition | 499 | 7 |
| ChiCTR | target disease | 170 | 18 |
| ITMCTR | target disease | 36 | 13 |
| Total | | 705 | 38 |

Five ITMCTR records carry a ChiCTR partner registration number and are counted once
(`Data/Unified/chictr_projmap.json`).

## Layout

```
Code/                     the pipeline, in run order
Data/Unified/             search log, raw responses, screening audit, extracted fields
Data/Unified/chictr_pages.zip  one crawled page per retrieved ChiCTR record (170)
Tables/                   Table 1-3 as emitted by the pipeline
Figures/                  Figure 1-4 as emitted by the pipeline
Manuscript.docx/.md       the manuscript this deposit supports
```

## Running it

```
python Code/60_search_registries.py        # ClinicalTrials.gov + ITMCTR searches
python Code/61_chictr_search.py            # ChiCTR search (headless Chrome)
python Code/66_chictr_extract.py           # rule-derived inclusion set + registry-read fields
python Code/62_rebuild_tables_figures.py   # Tables 1-3, Figures 1-4, all gates
python Code/63_descriptives.py             # the numbers quoted in the Results text
```

`64_verify_chictr.py` re-reads the included ChiCTR records from the live registry; it
is what the retained pages in `Data/Unified/chictr_pages.zip` were crawled with, so a
reader can check every extracted ChiCTR field without network access.

The ChiCTR scripts need a Chrome binary; set the `CHROME` environment variable if it
is not at the default Windows path. The searches are live queries: rerunning them
returns the registries as they stand on the day, which will differ from the
29 September 2026 snapshot reported here — the snapshot is what `Data/` holds.

`62_rebuild_tables_figures.py` exits non-zero if any of its 48 consistency checks
fails: every proportion stack must sum to 100%, every figure legend's n must equal the
number of source rows behind it, every value printed on a figure must be present in
the emitted table, and the inclusion audit must account for every retrieved record.

Requirements: Python 3 with `matplotlib`, `numpy` and `PIL`. No other dependency.
