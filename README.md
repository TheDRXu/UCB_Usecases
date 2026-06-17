# FDA Drug Label RAG Assistant

A retrieval-augmented generation (RAG) system that lets you ask plain English questions about FDA-approved drug labels and get instant, cited answers — grounded exclusively in official label text.

Built for UCB's epilepsy portfolio (Keppra / Briviact) as a proof of concept, but works with any drug on FDA DailyMed.

---

## What it does

You ask a question. It finds the most relevant sections from the FDA label. It passes them to an LLM. You get an answer with the exact source cited.

```
Q: What is the dose adjustment for renal impairment in levetiracetam?

A: For patients with mild renal impairment (50-80 mL/min): 500-1000mg every 12 hours.
   Moderate (30-50 mL/min): 250-750mg every 12 hours.
   Severe (below 30 mL/min): 250-500mg every 12 hours.
   ESRD on dialysis: 500-1000mg every 24 hours plus a 250-500mg supplemental dose post-dialysis.

   Source: levetiracetam — Section 2.5 Dosage Adjustments in Adult Patients with Renal Impairment
```

The model cannot make things up — it only answers from what's in the retrieved label sections.

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

## Example questions

**Dosing**
- "What is the starting dose of levetiracetam for adults?"
- "What dose adjustment is needed for a patient with severe renal impairment?"
- "What is the maximum daily dose of brivaracetam for adults?"

**Safety**
- "What psychiatric side effects should patients be warned about for levetiracetam?"
- "What dermatological reactions have been reported for brivaracetam?"
- "Can levetiracetam cause blood pressure changes in young children?"

**Comparative**
- "How does the suicidal ideation warning compare between the two drugs?"
- "Can brivaracetam and levetiracetam be taken together?"
- "Which drug has more clinical trial evidence for pediatric use?"

**Regulatory / MLR**
- "Can we claim levetiracetam has no drug-drug interactions?"
- "Is brivaracetam a controlled substance?"
- "Can a pregnant woman take levetiracetam?"

---

## Adding more drugs

Open `fda_label_parser.ipynb` and add drug names to `DRUG_LIST`:

```python
DRUG_LIST = [
    "levetiracetam",
    "brivaracetam",
    "cimicoxib",       # add any drug name here
    "lacosamide",
]
```

Drug names must match DailyMed search terms. You can verify availability at [dailymed.nlm.nih.gov](https://dailymed.nlm.nih.gov).

Re-run the parser notebook to generate a new `all_drugs_chunks.json`, then re-run the RAG notebook from Section 5 (embedding) to rebuild the index.

---

## Label sections included

The parser keeps only clinically meaningful sections and skips packaging, medguide, and product metadata noise.

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

## Known limitations

- **Generic questions without a drug name** produce lower retrieval scores (worst observed: 0.385). Be specific — "What are the psychiatric side effects of levetiracetam?" retrieves better than "What are the psychiatric side effects?"
- **ChromaDB is local only** — not suitable for multi-user production. Migrate to Amazon OpenSearch for production deployment.
- **Only 2 drugs indexed** in this POC. Expand `DRUG_LIST` in the parser notebook to add more.
- **No confidence threshold** — the system will answer even on low-score retrievals. A threshold of 0.5 is recommended for production to return "insufficient information" on poor matches.

---

## Roadmap

- [ ] Migrate vector store to Amazon OpenSearch
- [ ] Add confidence threshold and graceful fallback
- [ ] Build Streamlit UI for non-technical users
- [ ] Add audit logging to S3 for GxP compliance
- [ ] Expand corpus to PubMed for literature Q&A
- [ ] Hallucination detection via LLM-as-judge

---

## Data source

All label data comes from [FDA DailyMed](https://dailymed.nlm.nih.gov) — the official FDA drug label database. Data is free, public, and requires no login or license.

Labels are fetched live via the DailyMed REST API:
```
https://dailymed.nlm.nih.gov/dailymed/services/v2/spls.json?drug_name={drug_name}
```

---

## Cost estimate

Running the full 20-question evaluation costs approximately $0.03 using Amazon Nova Pro. At 1,000 queries per day in production, estimated cost is ~$1.50/day.

| Model | Use case | Approx cost per query |
|-------|----------|----------------------|
| amazon.nova-lite-v1:0 | Dev / testing | ~$0.0005 |
| amazon.nova-pro-v1:0 | Production / demo | ~$0.0015 |
