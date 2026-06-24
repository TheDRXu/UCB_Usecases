# FDA Drug Label RAG Assistant

A retrieval-augmented generation (RAG) system that lets you ask plain English questions about FDA-approved drug labels and get instant, cited answers — grounded exclusively in official label text.

Built for UCB's epilepsy portfolio (Keppra / Briviact) as a proof of concept, but works with any drug on FDA DailyMed.

---

## What it does

You ask a question. It finds the most relevant sections from the FDA label. It passes them to an LLM. You get an answer with the exact source cited. The model cannot make things up — it only answers from what's in the retrieved label sections.

---

## Performance (20-question evaluation)

| Metric | Result |
|--------|--------|
| End-to-end latency (avg) | 1.67s |
| Top-1 retrieval score (avg) | 0.742 |
| Best retrieval score | 0.903 |
| Citation compliance | 20/20 (100%) |
| Factual accuracy | 19/20 (95%) |
| Cost per 20 queries | ~$0.03 |

---

## Examples

**1. Dosing — Renal Impairment**
```
Q: What is the dose adjustment for renal impairment in levetiracetam?

A: Levetiracetam dosing must be adjusted based on creatinine clearance.
   Mild (50-80 mL/min): 500-1000mg every 12 hours.
   Moderate (30-50 mL/min): 250-750mg every 12 hours.
   Severe (below 30 mL/min): 250-500mg every 12 hours.
   ESRD on dialysis: 500-1000mg every 24 hours plus a 250-500mg supplemental dose post-dialysis.

   Source: levetiracetam — Section 2.5 Dosage Adjustments in Adult Patients with Renal Impairment
```

**2. Safety — Pregnancy**
```
Q: Can a pregnant woman take levetiracetam?

A: Levetiracetam is not contraindicated in pregnancy but requires careful monitoring.
   Plasma levels may decrease significantly during the third trimester, and dose adjustments
   may be required to maintain clinical response. Published data have not established an
   association with major birth defects or miscarriage. Women taking levetiracetam during
   pregnancy are encouraged to enroll in the NAAED Pregnancy Registry: 1-888-233-2334.

   Source: levetiracetam — Section 8.1 Pregnancy, Section 5.11 Seizure Control During Pregnancy
```

**3. Drug Interaction**
```
Q: Does brivaracetam interact with rifampin?

A: Yes. Co-administration with rifampin decreases brivaracetam plasma concentrations by
   approximately 45%, likely due to CYP2C19 induction. Prescribers should increase the
   brivaracetam dose by up to 100% (i.e., double the dosage) in patients receiving
   concomitant rifampin treatment.

   Source: brivaracetam — Section 7.1 Rifampin
```

**4. Cross-drug Comparison**
```
Q: Can brivaracetam and levetiracetam be taken together?

A: Yes, they can be taken together, but brivaracetam provided no added therapeutic benefit
   to levetiracetam when the two drugs were co-administered. In Studies 1 and 2,
   approximately 20% of patients were on concomitant levetiracetam, and BRIVIACT showed
   no added benefit in that subgroup.

   Source: brivaracetam — Section 7.4 Levetiracetam
```

**5. MLR Claim Check**
```
Q: Is brivaracetam a controlled substance?

A: Yes. BRIVIACT contains brivaracetam and is listed as a Schedule V controlled substance.

   Source: brivaracetam — Section 9.1 Controlled Substance
```

---

## Stack

| Component | Technology |
|-----------|-----------|
| Data source | FDA DailyMed API — free, no login |
| Embedding model | Amazon Titan Embed v2 via AWS Bedrock |
| Vector store | ChromaDB (local) |
| LLM | Amazon Nova Pro via AWS Bedrock |
| Orchestration | Python / boto3 |
| Region | ap-southeast-2 |

---

## Prerequisites

- Python 3.9+
- AWS account with Bedrock access enabled
- Bedrock Bearer Token (`AWS_BEARER_TOKEN_BEDROCK`)
- Models enabled in your region: `amazon.titan-embed-text-v2:0` and `amazon.nova-pro-v1:0`

To enable models: AWS Console → Bedrock → Model Access → enable Titan Embed v2 and Nova Pro.

---

## Setup

```bash
pip install boto3 chromadb requests
```

Clone the repo and place your chunks JSON file in the root directory. Then run the notebooks in order.

---

## Notebooks

Run these in order:

### 1. `fda_label_parser.ipynb`
Downloads and parses FDA drug labels from DailyMed into structured chunks.

- Fetches label XML via DailyMed API (no auth required)
- Extracts clinically relevant sections only — warnings, dosing, adverse reactions, pharmacokinetics, clinical studies
- Preserves hierarchy: every chunk knows its parent section
- Outputs `all_drugs_chunks.json`

```python
# Change this list to any drugs you want
DRUG_LIST = [
    "levetiracetam",
    "brivaracetam",
]
```

Each chunk looks like this:

```json
{
  "drug": "levetiracetam",
  "section": "Warnings and Precautions",
  "subsection": "5.2 Suicidal Behavior and Ideation",
  "title": "5.2 Suicidal Behavior and Ideation",
  "text": "Antiepileptic drugs (AEDs), including levetiracetam...",
  "loinc_code": "43685-7"
}
```

---

### 2. `fda_rag_bedrock.ipynb`
Embeds chunks, builds the vector index, and runs the full RAG pipeline.

**Section 2 — set your credentials:**
```python
os.environ['AWS_BEARER_TOKEN_BEDROCK'] = "your-bearer-token-here"
```

**Section 9 — model selection:**
```python
LLM_MODEL = "amazon.nova-pro-v1:0"       # best quality
# LLM_MODEL = "amazon.nova-lite-v1:0"    # cheaper, faster
```

The notebook walks through:
1. Install dependencies
2. Configure AWS credentials
3. Load chunks JSON
4. Format chunks for embedding
5. Embed using Titan Embed v2
6. Set up ChromaDB locally
7. Load chunks into ChromaDB
8. Test retrieval
9. Ask questions via Bedrock converse API
10. Run demo questions
11. Estimate cost

---

## Adding more drugs

Open `fda_label_parser.ipynb` and add drug names to `DRUG_LIST`:

```python
DRUG_LIST = [
    "levetiracetam",
    "brivaracetam",
    "cimicoxib",
    "lacosamide",
]
```

Drug names must match DailyMed search terms. You can verify availability at [dailymed.nlm.nih.gov](https://dailymed.nlm.nih.gov).

Re-run the parser notebook to generate a new `all_drugs_chunks.json`, then re-run the RAG notebook from Section 5 to rebuild the index.

---

## Label sections included

| LOINC Code | Section |
|------------|---------|
| 34067-9 | Indications and Usage |
| 34068-7 | Dosage and Administration |
| 34070-3 | Contraindications |
| 43685-7 | Warnings and Precautions |
| 34084-4 | Adverse Reactions |
| 43684-0 | Use in Specific Populations |
| 34088-5 | Overdosage |
| 34090-1 | Clinical Pharmacology |
| 43679-0 | Mechanism of Action |
| 43682-4 | Pharmacokinetics |
| 34092-7 | Clinical Studies |

---

## Data source

All label data comes from [FDA DailyMed](https://dailymed.nlm.nih.gov) — the official FDA drug label database. Free, public, no login required.

```
https://dailymed.nlm.nih.gov/dailymed/services/v2/spls.json?drug_name={drug_name}
```

---

## Cost estimate

| Model | Use case | Approx cost per query |
|-------|----------|----------------------|
| amazon.nova-lite-v1:0 | Dev / testing | ~$0.0005 |
| amazon.nova-pro-v1:0 | Production / demo | ~$0.0015 |

---

## Todo

- [ ] Get more drug data — expand corpus beyond levetiracetam and brivaracetam
- [ ] Migrate vector store to AWS OpenSearch Service
