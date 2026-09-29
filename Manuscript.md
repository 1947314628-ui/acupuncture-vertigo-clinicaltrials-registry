# Acupuncture clinical trial registration for vertigo: a descriptive multi-registry comparison of ClinicalTrials.gov, ChiCTR and ITMCTR (2015–2026)

Short title: Acupuncture-vertigo trial registration across three registries

Qin Zhang^1^, Tong Yin^2^, Yueping Huang^2^, Chuyun Chen^1,\*^

^1^ Department of Acupuncture and Moxibustion, The Affiliated Traditional Chinese Medicine Hospital, Guangzhou Medical University, Guangzhou, Guangdong, China

^2^ The Second Clinical Medical College of Guangzhou University of Chinese Medicine, Guangzhou, Guangdong, China

^\*^ Corresponding author. Email: chencyzwl@126.com

Email addresses: Qin Zhang, zhangqin@stu.gzucm.edu.cn; Tong Yin, 20221110329@stu.gzucm.edu.cn; Yueping Huang, hyp@bucm.edu.cn; Chuyun Chen, chencyzwl@126.com

## Abstract

Acupuncture is widely investigated for vertigo, but the registered trial base for this indication has not been characterised across registries. We searched ClinicalTrials.gov, the Chinese Clinical Trial Registry (ChiCTR) and the International Traditional Medicine Clinical Trial Registry (ITMCTR) on 29 September 2026, restricting every registry to its disease or condition field and applying the same six-concept vertigo block in each registry's own language of record (vertigo, dizziness, Meniere, BPPV, vestibular migraine, cervical vertigo; 眩晕, 头晕, 梅尼埃病, 耳石症, 前庭性偏头痛, 颈性眩晕). One acupuncture-family lexicon was applied to the registered intervention text of every retrieved record, and every retrieved record carried a documented inclusion decision. Blinding was harmonised by a stated rule, and recruitment status was mapped onto one vocabulary. The searches returned 705 disease-field records (499 ClinicalTrials.gov, 170 ChiCTR, 36 ITMCTR) and confirmed 38 registered acupuncture-vertigo trials (7, 18 and 13). Because the three platforms implement disease-field search differently, the retrieved totals are not equivalent denominators and no density ratio is reported. The sets differed in the subtypes studied (cervical vertigo in 8 of 18 ChiCTR trials and none of the 7 ClinicalTrials.gov trials; posterior circulation ischaemia vertigo in 4 of 13 ITMCTR trials), in the reporting of blinding (unstated in 0 of 7, 4 of 18 and 13 of 13 trials) and in the outcome instruments recorded, the Dizziness Handicap Inventory being the only instrument recorded in all three sets (3 of 7, 11 of 18 and 1 of 13). Five ITMCTR records carried a ChiCTR partner registration number and were counted once. Describing this evidence base reliably requires searching more than one registry, stating the search field used, and registering the masked parties rather than a blinding category alone.

**Keywords:** acupuncture; vertigo; clinical trial registration; ClinicalTrials.gov; ChiCTR; ITMCTR; research reporting

## Introduction

Vertigo is among the most common clinical complaints, with an estimated lifetime prevalence exceeding 20% [1]. Its clinical spectrum includes benign paroxysmal positional vertigo (BPPV), vestibular migraine, Meniere disease, vestibular neuritis and persistent postural-perceptual dizziness (PPPD), each with distinct pathophysiology and treatment approaches [2,3,4]. Standard treatment remains aetiology-dependent: canalith repositioning manoeuvres are first-line for BPPV, though residual dizziness and recurrence are common [3]; pharmacotherapy provides symptomatic relief with limited evidence for long-term efficacy [5]; and vestibular rehabilitation requires sustained adherence and specialised training. Acupuncture has been investigated as a non-pharmacological alternative across several vertigo subtypes. Systematic reviews have reported positive effects for posterior circulation infarction vertigo, mediated in part through improved vertebrobasilar haemodynamics [6], and for cervical vertigo [7], although these reviews consistently note small sample sizes, heterogeneous outcome measures and inconsistent blinding as limitations. The evidence base for acupuncture in vertigo has not, however, been characterised at the trial registration level.

Clinical trial registries provide structured data for characterising research activity within a disease domain. ClinicalTrials.gov is the largest global registry [8]. The Chinese Clinical Trial Registry (ChiCTR), a WHO-recognised primary registry, has documented rapid growth in acupuncture trial registration [9]. The International Traditional Medicine Clinical Trial Registry (ITMCTR), designated a WHO primary registry in February 2023, is organised by therapeutic theme and now serves as a dedicated platform for traditional medicine trial registration following the July 2024 transition of such registrations from ChiCTR [10]. Cross-sectional analyses of individual registries have characterised real-world studies [8], acupuncture trial growth [9] and interventional trial characteristics [11]. No study, however, has compared acupuncture trial registration for a specific disease indication across more than one registry, and no prior analysis of acupuncture-vertigo registration has included ITMCTR as a data source.

Comparing registries requires care. The three platforms expose different search fields, index different record sets and attract different investigator populations, so a comparison is only interpretable if the search scope is held constant and the residual differences are stated rather than smoothed over. We therefore searched all three registries through their disease or condition field alone, applied one word list and one screening rule to every retrieved record, and report the resulting counts descriptively rather than as ratios of research density.

This study aimed to: (1) identify all registered acupuncture clinical trials for vertigo on ClinicalTrials.gov, ChiCTR and ITMCTR under a single search scope; (2) describe and compare the trial characteristics, disease subtypes, intervention modalities and recorded outcome instruments across the three registries; and (3) publish the full search log and a record-level inclusion audit so that every count can be reproduced or contested.

## Methods

### Study Design and Reporting

This registry-based cross-sectional analysis is reported in accordance with the Strengthening the Reporting of Observational Studies in Epidemiology (STROBE) guidelines [12]. Three clinical trial registries were searched: ClinicalTrials.gov (United States National Library of Medicine), ChiCTR and ITMCTR. All searches reported here were executed on 29 September 2026. The study is a secondary analysis of publicly accessible, de-identified registry records and required no ethics approval.

### Search Strategy and Scope

One search scope was used on all three platforms: the registry's disease or condition field. The same six-term vertigo block was applied in each registry's own language of record, one term per concept per language, and no term was applied to any other field. The two language blocks are held concept for concept in parallel; an earlier version of this analysis had five Chinese terms against six English ones, and the missing concept removed a registered acupuncture trial for vestibular migraine from the Chinese results.

On ClinicalTrials.gov the search was executed through API v2 with the condition-field parameter `query.cond` and the unquoted expression `vertigo OR dizziness OR Meniere OR BPPV OR vestibular migraine OR cervical vertigo`, with total counts obtained via `countTotal=true` and all records retrieved by page token. The individual term counts were 436, 436, 76, 88, 50 and 32 respectively, and the OR-combined condition-field total was 499. This 499 is the denominator used throughout; it is a condition-field count, and it supersedes the all-field count used in earlier versions of this analysis.

On ChiCTR the six Chinese terms 眩晕, 头晕, 梅尼埃病, 耳石症, 前庭性偏头痛 and 颈性眩晕 were applied to the target-disease field (`studyailment`) through the registry's public search interface, returning 102, 40, 33, 1, 12 and 10 records respectively and 170 unique records after cross-term deduplication. ChiCTR serves its search results behind a web application firewall, so the pages were rendered with a scripted browser; the script and the returned counts are included in the search log.

On ITMCTR the same six Chinese terms were applied to the target-disease field (`dynamicQueries[target_disease]`) through the platform's own search endpoint, returning 31, 6, 0, 0, 1 and 5 records and 36 unique records after deduplication. The ITMCTR search endpoint returns the full registration record for each hit; no separate detail endpoint is exposed. The registry is at http://itmctr.ccebtcm.org.cn/ (an earlier manuscript cited https://www.itmctr.cn, which does not resolve).

The complete search log, including the exact expressions, the per-term counts and the retrieval date, is provided as S1 Text. No count in this manuscript was derived by arithmetic; every denominator is a total returned by the registry at the time of search.

### Eligibility and Screening

A record was included as a registered acupuncture-vertigo trial when both of the following held:

1. The registered condition field named a vertigo or dizziness disorder. This was verified record by record; trials in which a vertigo term appeared only in narrative text, in a secondary outcome or in an adverse-event description were excluded.
2. The registered intervention was an acupuncture-family intervention, that is, an acupuncture-family term appeared in the registered intervention names, in the registered arm labels, or — where the registry left those generic — in the registered title.

Records were excluded when the registered intervention was a non-acupuncture modality and named no needling modality (transcutaneous auricular vagus nerve stimulation, tuina or other manual therapy, chiropractic, repositioning manoeuvres, or a non-acupoint injection such as a lidocaine or blood-patch procedure), when the registered study type was observational or diagnostic rather than interventional, or when the record was withdrawn or terminated.

On the two Chinese registries screening was applied to each retrieved record, not to a pre-selected list: the screen reads the registered intervention field and the registered title, so a trial whose title avoids the word acupuncture is still found. A candidate set that had been assembled by hand was used in earlier versions of this analysis; re-screening the retrieved records against the rule above found a registered acupuncture trial for vestibular migraine that the hand list had missed, and the hand list is no longer a data source.

Screening is automated from the registry fields and then reviewed record by record. Every retrieved record carries a decision and a reason in the inclusion audit provided as S2 File; the audit contains exactly the 499, 170 and 36 retrieved records, and the included and excluded counts for each registry sum to its retrieved total.

### Data Extraction

ClinicalTrials.gov fields were extracted programmatically through API v2: identifier, first-submission date, overall status, allocation, masking and who was masked, planned enrolment, conditions, intervention and arm names, primary outcome measures, locations and title. ChiCTR fields were read from the live registry record of every retrieved record (registered condition, study type, registered design, randomisation method, blinding, planned sample size, intervention, outcome measures, registration date, sponsor), and the raw registry pages were retained alongside the extraction file. ITMCTR fields were taken from the values returned by the platform's search endpoint, which include the blinding field, the randomisation procedure, the planned sample size, the target disease, the study phase and the objectives.

For ChiCTR the trial total is not shown as a single field: the record form states the size of each arm. Planned enrolment for ChiCTR records is therefore the sum of the registered arm sizes. This sum was verified against the registry's WHO-format Trial Registration Data Set export, which states the same arm sizes in English, for the 15 included records for which that export was available; all 15 agreed.

No value in this manuscript is transcribed by hand from a registry page, and none is carried over from an earlier version of the analysis.

### Blinding Classification

Blinding was harmonised across the three platforms by an explicit rule, because the platforms describe it in incompatible vocabularies and default text. A trial was classified as:

- **Double-blind** when participants and at least one of investigators, care providers or outcome assessors were masked;
- **Single-blind** when participants alone were masked;
- **Assessor-blinded** when one or more assessors, investigators or care providers were masked but participants were not;
- **Other or partial** when blinding was described but the masked parties could not be identified;
- **Open-label or none** when the record stated that no masking was used;
- **Not stated** when the record contained no blinding description.

On ClinicalTrials.gov the registry's masking type and masked-party fields were used directly; notably, a record registered as `DOUBLE` with only `INVESTIGATOR` and `OUTCOMES_ASSESSOR` named is classified here as assessor-blinded rather than double-blind, because participants were not masked. On ChiCTR and ITMCTR the free-text blinding field was classified by the rule above, so records whose text reads "single-blind" but names both participants and assessors are classified as double-blind.

Recruitment status was likewise mapped onto one vocabulary before comparison, because the Chinese registries return it as a status label in Chinese rather than in the terms ClinicalTrials.gov uses: 尚未开始 to Not yet recruiting, 正在进行 to Recruiting and 结束 to Completed, with a status the record does not state reported as not stated (ClinicalTrials.gov reports those records as UNKNOWN). The mapping is one-to-one and no record was reclassified by judgement.

### Cross-Registry Deduplication

ITMCTR publishes a partner-registry number for records registered elsewhere. An ITMCTR record whose partner number matched an included ChiCTR record was excluded from the ITMCTR set and counted once under ChiCTR. Five such pairs were identified, and no ITMCTR record in the included set carries a partner number that resolves to an included ChiCTR record. No record in the ClinicalTrials.gov set was duplicated in either Chinese registry.

### Statistical Analysis

Counts and percentages describe categorical variables; medians and ranges describe planned enrolment. No inferential test, trend model or completeness score is reported: with 7, 18 and 13 confirmed trials, and with disease-field search semantics that differ between platforms, the data do not support between-registry statistical comparison, and reporting one would imply a precision the design cannot deliver. Every figure is generated from the same screened record set that produces the tables, and the generation script fails rather than emit a chart when a plotted value cannot be traced to the source tables.

### Data and Code Availability

The search scripts, the screening audit, the extraction forms, the table and figure generation code, and the search log are available in the public repository https://github.com/1947314628-ui/acupuncture-vertigo-clinicaltrials-registry, archived at DOI 10.5281/zenodo.21110650 (concept DOI, all versions) under a CC BY 4.0 licence. The registry responses themselves are public records of ClinicalTrials.gov, ChiCTR and ITMCTR, and the retained ChiCTR pages are included in the deposit.

## Results

### Search Results

The unified disease-field searches returned 705 records: 499 from ClinicalTrials.gov, 170 from ChiCTR and 36 from ITMCTR. Screening confirmed 38 registered acupuncture-vertigo trials: 7 on ClinicalTrials.gov, 18 on ChiCTR and 13 on ITMCTR (Table 1, Fig 1). The inclusion audit records a decision and a reason for each of the 705 retrieved records.

The three totals are not equivalent denominators. ClinicalTrials.gov was searched on its condition field, which indexes a large international registry whose records are mostly not traditional-medicine trials; ChiCTR and ITMCTR were searched on their target-disease field, which indexes smaller platforms with different indexing and different contributor populations. The retrieved totals therefore reflect the size and indexing of each platform rather than the volume of acupuncture research in a country, and no cross-registry density ratio is computed or reported anywhere in this manuscript.

**Table 1.** Records retrieved and confirmed acupuncture-vertigo trials, by registry, under a unified disease-field search scope. Counts are as returned by each registry on 29 September 2026; they are not equivalent denominators (see Methods).

@TABLE:Tables/Table1_Search_Results.csv

@FIG:Figures/Figure_1_Registry_Comparison.png

**Fig 1.** Trial volume by registry under the unified search scope: disease-field records retrieved (light bars) and confirmed acupuncture-vertigo trials (dark bars), logarithmic scale.

### ClinicalTrials.gov

Seven confirmed acupuncture-vertigo trials were registered between 2015 and 2025 (1 in 2015, 2 in 2020, and 1, 1 and 2 in 2023, 2024 and 2025 respectively). Median planned enrolment was 100 participants (range 60–345). Five trials used a randomised allocation and two were recorded as non-randomised or did not state an allocation. Status at the time of search was completed for 4 trials, recruiting for 1, and not stated for 2. Blinding was double-blind in 3 trials, assessor-blinded in 2 and open-label in 2; no record was silent on blinding.

Three trials carried a named vestibular subtype, BPPV, vestibular migraine and Meniere disease, one each; the remaining four registered sensorineural hearing loss with vertigo, hemifacial spasm with postoperative dizziness, and, in two trials, only a general dizziness or vertigo condition, and so could not be assigned to a named subtype. Manual acupuncture was the registered intervention in 5 trials, acupoint injection in 1 and transcutaneous electrical acupoint stimulation in 1. The Dizziness Handicap Inventory was recorded as an outcome in 3 trials and a visual analogue scale for dizziness in 4. Five trials were located in China, one in Taiwan, and one recorded no location. All 7 trials are individually listed with their inclusion reason in the audit.

### ChiCTR

Eighteen confirmed acupuncture-vertigo trials were registered between 2016 and 2026: 1 in 2016, 2 each in 2020, 2021 and 2022, 5 in 2023, 5 in 2024 and 1 in 2026. Median planned enrolment was 108 participants (range 60–360). All 18 stated a randomised design, and the registered design field read "randomised parallel control" for all 18. Status at the time of search was not yet recruiting for 10 trials, recruiting for 6 and completed for 2.

Blinding was double-blind in 3 trials (16.7%), single-blind in 1 (5.6%), assessor-blinded in 4 (22.2%), described but unclassifiable in 1 (5.6%), open-label in 5 (27.8%) and not stated in 4 (22.2%). The three double-blind trials are ChiCTR2200056229, whose blinding text names participants, assessors and the statistician, and ChiCTR2400080759 and ChiCTR2300079281, which name participants and assessors but are recorded by the registry under the single-blind category; under the rule stated in the Methods these are double-blind. Four further records name assessors, statisticians, data collectors or analysts but not participants and are therefore classified as assessor-blinded; ChiCTR2400080734 states explicitly that the acupuncturists and the participants could not be masked, which is why it is not counted as double-blind.

Cervical vertigo was the most frequent subtype (8 of 18 trials, 44.4%), followed by BPPV (4, 22.2%), posterior circulation ischaemia vertigo (3, 16.7%), vestibular vertigo (1), vestibular migraine (1) and one record whose registered condition named only dizziness or vertigo. No ChiCTR record was classified as Meniere disease. The registered interventions named manual acupuncture in 15 trials, electroacupuncture in 3, acupotomy in 2 and moxibustion in 1; a record may name more than one modality. Recorded outcome instruments included the Dizziness Handicap Inventory in 11 trials, transcranial Doppler in 6, a visual analogue scale in 4 and magnetic resonance imaging in 2. All 18 trials were conducted at Chinese institutions.

### ITMCTR

Thirteen confirmed acupuncture-vertigo trials were registered between 2022 and 2026: 2 in 2022, 3 in 2023, 6 in 2025 and 2 in 2026. Median planned enrolment was 76 participants (range 60–234). Twelve trials used a randomised design and one was single-arm. Status at the time of search was not yet recruiting for 6 trials, completed for 5 and recruiting for 2.

The registered blinding field was empty in all 13 records, so all 13 are classified as not stated. This is a property of the included set rather than of the platform: 6 of the 36 records retrieved from ITMCTR did contain blinding text, including one that described masking of participants and investigators, so the field is available and was left unfilled by these registrants.

Posterior circulation ischaemia vertigo was the most frequent subtype (4 of 13 trials, 30.8%), followed by cervical vertigo (3, 23.1%), BPPV (1), peripheral vertigo (1), PPPD (1), cerebral small vessel disease-related dizziness (1), post-stroke vascular vertigo (1) and vestibular migraine (1). PPPD, cerebral small vessel disease-related dizziness and post-stroke vascular vertigo did not appear in either of the other two sets. The registered interventions named manual acupuncture in 9 trials, acupressure or press-needle in 2, moxibustion in 1, acupoint injection or embedding in 1 and another acupuncture-family modality in 2. The Dizziness Handicap Inventory and transcranial Doppler were each recorded in 1 trial and magnetic resonance imaging in 2, and no ITMCTR trial recorded a visual analogue scale. All 13 trials were conducted at Chinese institutions.

Five further ITMCTR records were registered acupuncture-vertigo trials that carried a ChiCTR partner registration number (ITMCTR2200005589, ITMCTR2200005551, ITMCTR2100004929, ITMCTR2100004431 and ITMCTR2000003943, partnered with ChiCTR2200056229, ChiCTR2200055867, ChiCTR2100047162, ChiCTR2000039716 and ChiCTR2000036713 respectively). These were counted once, under ChiCTR, and are listed with that reason in the audit.

### Comparison Across Registries

Table 2 and Fig 2 set out the comparison. The clearest difference between the sets is in the disease subtypes studied. Cervical vertigo accounted for 8 of 18 ChiCTR trials and none of the 7 ClinicalTrials.gov trials, while Meniere disease appeared only in the ClinicalTrials.gov set and vestibular migraine appeared once in each of the three sets. Posterior circulation ischaemia vertigo was the commonest ITMCTR subtype (4 of 13) and the third commonest on ChiCTR (3 of 18). The pattern is consistent with different diagnostic frameworks and different referral populations rather than with a difference in acupuncture practice alone, and it means that a synthesis restricted to any single registry samples a different set of vertigo aetiologies.

Study size and design were broadly similar across the three sets, with median planned enrolment between 76 and 108 participants and randomised allocation recorded in 5 of 7, 18 of 18 and 12 of 13 trials. Blinding, by contrast, differed sharply and in a way that limits comparison: no ClinicalTrials.gov trial was silent on blinding, 4 of 18 ChiCTR trials were, and all 13 ITMCTR trials were. Fig 3 shows the blinding and status distributions.

Outcome instruments overlapped only partly. The Dizziness Handicap Inventory was the only instrument recorded in all three sets (3 of 7, 11 of 18 and 1 of 13). Transcranial Doppler and imaging outcomes appeared on the Chinese registries (6 and 2 on ChiCTR, 1 and 2 on ITMCTR) and not at all on ClinicalTrials.gov, whereas the visual analogue scale appeared on ClinicalTrials.gov (4 of 7) and ChiCTR (4 of 18) but not on ITMCTR.

**Table 2.** Characteristics of confirmed acupuncture-vertigo trials by registry. Blinding classes follow the harmonisation rule in the Methods; the "Commonest subtype" column reports a tie explicitly rather than choosing one subtype.

@TABLE:Tables/Table2_Characteristics_Comparison.csv

**Table 3.** Registered acupuncture modalities and recorded outcome instruments by registry, counted per trial.

@TABLE:Tables/Table3_Intervention_Profiles.csv

@FIG:Figures/Figure_2_Disease_Spectrum.png

**Fig 2.** Registered vertigo subtypes by registry, as a percentage of each registry's confirmed acupuncture-vertigo trials. BPPV = benign paroxysmal positional vertigo; PCI = posterior circulation ischaemia; PPPD = persistent postural-perceptual dizziness; CSVD = cerebral small vessel disease.

@FIG:Figures/Figure_3_Methodological_Quality.png

**Fig 3.** A: blinding classification by registry, following the harmonisation rule in the Methods. B: recruitment status at the time of search.

### Temporal Pattern of the Retrieved Records

Fig 4A shows the annual number of ClinicalTrials.gov records retrieved by the condition-field search, 1999–2026; the 2026 count covers the year to 29 September and is not comparable with complete years. No trend model is fitted to these counts. Fig 4B shows the annual number of confirmed acupuncture-vertigo trials in each registry. On ChiCTR, confirmed trials rose from 1 in 2016 to 5 in 2023, and on ITMCTR the 13 confirmed trials fall in 2022–2026, with 8 of them in 2025–2026. The ClinicalTrials.gov confirmed trials are spread thinly across 2015–2025, with no year contributing more than 2. These are counts, not rates, and no comparison of trend between registries is made, because the confirmed sets are too small and the observation windows do not coincide.

@FIG:Figures/Figure_4_Annual_Trends.png

**Fig 4.** A: annual records retrieved from ClinicalTrials.gov by condition-field search, 1999–2026 (2026 partial). B: annual confirmed acupuncture-vertigo trials by registry.

## Discussion

This descriptive multi-registry comparison identified 38 registered acupuncture-vertigo trials under a single disease-field search scope: 7 on ClinicalTrials.gov, 18 on ChiCTR and 13 on ITMCTR. The three sets differ systematically in the disease subtypes studied, in whether blinding is reported at all, and in the outcome instruments recorded. Those differences, rather than a difference in research volume, are the finding.

The disease-spectrum difference is the most consequential for evidence synthesis. Cervical vertigo accounted for 44.4% of the ChiCTR set and none of the ClinicalTrials.gov set, while Meniere disease was recorded only on ClinicalTrials.gov and posterior circulation ischaemia vertigo was the single commonest subtype on ITMCTR. This registry-dependent distribution is consistent with the differing diagnostic frameworks and referral patterns recognised across the two traditions [2,7]. A meta-analysis that restricts itself to one registry therefore pools a different mix of aetiologies than one that searches all three, and the difference is large enough to change a pooled estimate rather than merely widen its confidence interval. The heterogeneity also bears on outcome selection: the Dizziness Handicap Inventory was the only instrument recorded in all three sets [13], which supports its use as a cross-registry common metric, while the broader divergence of instruments, including the use of transcranial Doppler and imaging outcomes on the Chinese platforms, reflects the absence of a vertigo-specific core outcome set [14].

Blinding reporting, rather than blinding practice, is where the registries diverge most sharply. No ClinicalTrials.gov trial omitted the field, 4 of 18 ChiCTR trials did, and all 13 ITMCTR trials did. Because the ITMCTR record structure does contain a blinding field, and six of the 36 records retrieved from that platform used it, the empty field is a reporting choice by registrants rather than a platform limitation. It is worth being precise about what this does and does not mean: an unreported blinding status is not evidence of absent blinding, but it does mean that nearly a quarter of the ChiCTR record base and the whole ITMCTR record base cannot be assessed for this design feature from the registration alone. Registration quality in this domain has been reported to be uneven before [15]; the present data localise the problem to one field on one platform rather than to registration as a whole.

The five cross-registered pairs, all between ChiCTR and ITMCTR, are a further practical finding. ITMCTR publishes the partner registration number, so the duplication is resolvable from the record itself; without that field, a multi-registry count would double-count these trials and, because they differ in which fields are filled, might also double-count them inconsistently.

Several limitations follow from what was and was not done. First, the confirmed sets are small, 7, 18 and 13, and no inferential or trend analysis is reported; the counts are descriptive and the subgroups within them, particularly the ITMCTR subtypes with one trial each, should not be read as rates. Second, the search scope was unified but the fields are not identical constructs: ClinicalTrials.gov's condition field and the Chinese registries' target-disease field index different record populations with different indexing rules, and the retrieved totals of 499, 170 and 36 reflect platform size as much as research activity. This is why no density ratio is reported; it is also why the retrieved totals should not be compared with one another as measures of national research output. Third, the automated screening used a word list, and a trial registered without any acupuncture-family term in its intervention, arm labels or title would have been missed; the alternative, searching all fields, is what produced the unreproducible numerator in earlier versions of this analysis, and we judged a stated scope with a full audit to be the better trade-off. The two language blocks of the vertigo word list are held in parallel for the same reason: a concept present on one side and absent on the other removes records silently, which is how an earlier version of this analysis came to report vestibular migraine as registered only on ClinicalTrials.gov. Fourth, cross-registry deduplication depends on ITMCTR populating its partner-registry number, which it did for the five known pairs but need not do for all. Fifth, the analysis covers registration records and not published results; the relationship between registration quality and eventual publication [16] could not be examined in a set of this size.

Two recommendations follow. First, a descriptive study of acupuncture trial registration should search more than one registry and should state the search field it used, because the apparent disease spectrum depends on which registry is consulted. Second, blinding status should be a required field at registration on the Chinese platforms, and reporting should name the masked parties rather than the category alone: one ChiCTR record in this set was registered as single-blind while naming participants and outcome assessors, a description that under the conventional definition is double-blind, and one ClinicalTrials.gov record was registered as "double" while naming only investigators and assessors. The vocabulary mismatch is not cosmetic; it changes how a trial is counted.

## Conclusions

Under one disease-field search scope, 38 registered acupuncture-vertigo trials were identified across three registries: 7 on ClinicalTrials.gov, 18 on ChiCTR and 13 on ITMCTR. The sets differ systematically in the vertigo subtypes studied, in whether blinding is reported, and in the outcome instruments recorded, so the picture of acupuncture research for vertigo depends on which registry is consulted. Blinding status was unstated for all 13 ITMCTR trials and 4 of 18 ChiCTR trials, and the disease spectrum recorded on each platform differed substantially. Multi-registry search with a stated search field, and a required, named-parties blinding field, are the minimum conditions for describing this evidence base reliably.

## Acknowledgments

**STRICTA reporting:** This study is a registry-based analysis and does not directly involve acupuncture interventions on human participants. For reporting of acupuncture-specific information extracted from trial registrations, the authors consulted the STRICTA checklist [17] to guide data extraction categories including needling modality classification and treatment regimen documentation. **Generative AI disclosure:** During the preparation of this work, the authors used Claude (Anthropic) and DeepSeek to assist with code development and manuscript editing. After using these tools, the authors reviewed and edited the content and take full responsibility for the content of the publication.

## References

1. Edlow JA, Carpenter C, Akhter M, Khoujah D, Marcolini E, Meurer WJ, et al. Guidelines for reasonable and appropriate care in the emergency department 3 (GRACE-3): Acute dizziness and vertigo in the emergency department. Acad Emerg Med. 2023;30(5):442-486. doi:10.1111/acem.14728
2. Lempert T, Olesen J, Furman J, Waterston J, Seemungal B, Carey J, et al. Vestibular migraine: Diagnostic criteria (Update). J Vestib Res. 2022;32(1):1-6. doi:10.3233/VES-201644
3. Cole SR, Honaker JA. Benign paroxysmal positional vertigo: Effective diagnosis and treatment. Cleve Clin J Med. 2022;89(11):653-662. doi:10.3949/ccjm.89a.21057
4. Basura GJ, Adams ME, Monfared A, Schwartz SR, Antonelli PJ, Burkard R, et al. Clinical practice guideline: Ménière's disease. Otolaryngol Head Neck Surg. 2020;162(2_suppl):S1-S55. doi:10.1177/0194599820909438
5. Rogers TS, Noel MA, Garcia B. Dizziness: Evaluation and management. Am Fam Physician. 2023;107(5):514-523. PMID: 37192077
6. Li B, Zhao Q, Du Y, Li X, Li Z, Meng X, et al. Cerebral blood flow velocity modulation and clinical efficacy of acupuncture for posterior circulation infarction vertigo: A systematic review and meta-analysis. Evid Based Complement Alternat Med. 2022;2022:3740856. doi:10.1155/2022/3740856
7. Mai W, Bu XZ, Miao FR, Rui JL, Huang LL, Zhao XJ, et al. [Moxibustion at Baihui combined with acupuncture for cervical vertigo: A meta-analysis and trial sequential analysis]. Zhen Ci Yan Jiu. 2023;48(1):95-101. Chinese. doi:10.13702/j.1000-0607.20211054
8. Li Y, Tian Y, Pei S, Xie B, Xu X, Wang B. Worldwide trends in registering real-world studies at ClinicalTrials.gov: A cross-sectional analysis. Int J Gen Med. 2023;16:1123-1136. doi:10.2147/IJGM.S402478
9. Li C, Zhang J, Cui Y, Zhang C, Gao H. Acupuncture clinical trials in the Chinese Clinical Registry: Growth, regional disparities, and standardization challenges. Med Acupunct. 2025;37(5):423-424. doi:10.1089/acu.2025.0040
10. Liang N, Zhang Y, Zhang X, Yan L, Zhao C, Yang S, et al. International Traditional Medicine Clinical Trial Registry: A meaningful initiative and its future development. J Evid Based Med. 2024;17(3):486-489. doi:10.1111/jebm.12651
11. Sullenger RD, Clare RM, Abbasi AB, Chiswell KE, Curtis LH, Hammill BG, et al. Characteristics of interventional clinical trials registered in ClinicalTrials.gov, 2018-2023. J Clin Transl Sci. 2026;10(1):e66. doi:10.1017/cts.2026.10701
12. von Elm E, Altman DG, Egger M, Pocock SJ, Gøtzsche PC, Vandenbroucke JP. The Strengthening the Reporting of Observational Studies in Epidemiology (STROBE) statement: Guidelines for reporting observational studies. Lancet. 2007;370(9596):1453-1457. doi:10.1016/S0140-6736(07)61602-X
13. Jacobson GP, Newman CW. The development of the Dizziness Handicap Inventory. Arch Otolaryngol Head Neck Surg. 1990;116(4):424-427. doi:10.1001/archotol.1990.01870040046011
14. Boreel MME, van Esch BF, van Beers MA, Kaski D, Bruintjes TD, van Benthem PPG. Developing a core outcome set for Menière's disease trials, the COSMED study: A scoping review on outcomes used in existing trials. Front Neurol. 2025;16:1516350. doi:10.3389/fneur.2025.1516350
15. Viergever RF, Ghersi D. The quality of registration of clinical trials. PLoS One. 2011;6(2):e14701. doi:10.1371/journal.pone.0014701
16. Matsuura Y, Takazawa Welch N, Sakai T, Tsutani K. Clinical trial registration, and publication in acupuncture studies: A systematic review. Integr Med Res. 2020;9(1):56-61. doi:10.1016/j.imr.2020.01.008
17. MacPherson H, Altman DG, Hammerschlag R, Youping L, Taixiang W, White A, et al. Revised STandards for Reporting Interventions in Clinical Trials of Acupuncture (STRICTA): Extending the CONSORT statement. PLoS Med. 2010;7(6):e1000261. doi:10.1371/journal.pmed.1000261

## Supporting information

**S1 Checklist.** STROBE checklist for this cross-sectional study of trial registration records.

**S1 Text.** Search log: the exact search expression, the per-term returned count and the retrieval date for each of the three registries, together with the rerunnable search scripts.

**S2 File.** Inclusion decisions (CSV): one row per retrieved record (499 ClinicalTrials.gov, 170 ChiCTR, 36 ITMCTR) giving the registered condition, the inclusion or exclusion decision and the reason for it.

**S3 File.** ChiCTR screening decisions for all 170 retrieved records (CSV).

**S4 File.** Extracted fields of the 18 included ChiCTR records (CSV), as read from the registry record.

**S5 File.** Retained ChiCTR registry pages (ZIP): one crawled page per retrieved ChiCTR record, with the parsing script that produced the extracted fields.
