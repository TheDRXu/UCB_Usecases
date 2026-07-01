import json
import os
import boto3
import pandas as pd
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# ── Config ───────────────────────────────────────────────────────────────────
BEARER_TOKEN = os.environ.get("AWS_BEARER_TOKEN_BEDROCK", "bedrock-api-key-YmVkcm9jay5hbWF6b25hd3MuY29tLz9BY3Rpb249Q2FsbFdpdGhCZWFyZXJUb2tlbiZYLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFTSUE0WDZWRFZOWU5NSEE2SjM0JTJGMjAyNjA2MzAlMkZhcC1zb3V0aGVhc3QtMiUyRmJlZHJvY2slMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI2MDYzMFQwNTQzMTVaJlgtQW16LUV4cGlyZXM9NDMyMDAmWC1BbXotU2VjdXJpdHktVG9rZW49SVFvSmIzSnBaMmx1WDJWakVQYiUyRiUyRiUyRiUyRiUyRiUyRiUyRiUyRiUyRiUyRndFYURtRndMWE52ZFhSb1pXRnpkQzB5SWtnd1JnSWhBSWZVcjFTSzNkTWEyNFZLNTMlMkJaNngzMXFTU3ZRQ2xUOFNNdzVBYiUyRnZ5SEFBaUVBNUViMjM3dWhOS1E5aG1vdWUlMkJ4OTVYR3Q5VkV0YWxkc01QTlJOMDlyZ2RvcWtBVUl2JTJGJTJGJTJGJTJGJTJGJTJGJTJGJTJGJTJGJTJGJTJGQVJBQUdndzROell3T0RNek9URXpORFFpRExYOUwycDRwQjhIQ1M0RlppcmtCQUhCc09CU1VQcm1pUzM2VnVHM3p2YzJaZERpVVZCT0dsWmUzZXVaM3FYT2Rvc1pBdGtZQmw2JTJGV1RaSGJ3eGJDQ2M4eWs2bHptMDZ6cmdDRnU4NGM1R0RuOFhnYUx0QllhMHVHZEpyaU9USldER2FUTFdIQ055S3JmMUR3NllUNVhvSmRoVTRsUFNOJTJCcVhPM2tDcmZLeXlQYXJvTGtXemtHZHVkN2FtaVNBN2RIMGp5NTNGS0toeW9aRHhoemFIdGNHWm42SUZmRldWeU5yQ2dSY2FOU3p5ZzFJSmV4eFdLSzdGREFDbE1MMGNvUzRaOFh2UUxhWjZ2OGNWYm5UWCUyRlo3UGE2Y3BqaVlIVEtSMjNQd2xIbjNSREozaGNaMDcyV2QlMkZOeFZ1Rlc5OE1uWmdEU1Nkc1NTdDJReUVNUHZVNDByaE56RkNxSUR4Zkw5c25JazNzcU1FM1JOc2FwTm1CcVVYd1BkSXdDNGpsTWJDam1aOTNMR0ZaRkMyT3Nra2M0cUhxVXVXVEx4YkkxUmtXSCUyRklobWlZem93WFNZd2NURjdqZXBnM0Y1bTFPYmlsQW9HNUF5cFd3V2J0QWp1QVVmYWZMdTlhMzRPV29WN0VYcHNSTkRKQlZpNVl5OXNIR3VrckVYOGVFOGtQcU91Szg1RXNVN01pekZLU3hLOTYyVWNzaUg2SjIlMkZKOTdhSFQlMkJCJTJCQk5vcE1WWUNnWGElMkJRRWtqRXRFOFhtc0F0clZySGRJRjlWSFVmVUZNUm96YkVycmRYRUs3S05mdEZNU0pLN1M3UlNDSkMzS2hzYUZCdlRnVVB0eSUyQnlZcDk4dEFqMjhvN0xKWWklMkJPUmh2Y2MyNVU5QnN0T1JVV3cxY2FSMlh4QzB0OEFHYThBQUZTYnJ5UVVkY0J1U0xqT2NwR2x0bFloMXhycGtmVldkajIyaG1OZnYwWGw3eFY2OWJpNnolMkJDQ1VGRmRKRmJwNWhnSldPaUw2UjFNaHJITmFKYmFxNFl4U3cwU2x4NzdJM09yeGxpMmc1OUhmQ0IlMkJvajNJNDNxeENFSWJxVDRScUx3blJKQ20lMkZkOXd6NjNpeWlXNGdkUlREZnJvM1NCanJHQXM4a25nRE1TQkgyQ2c5anA1U2NoN05kdFFhMmVqWnVrcENVOGNONmN1aVRwT21vUm9rQWt5UUhUTk0lMkJyQjNZOXVJaGZENzVJOFQwYkFBSldxUFcwellyZFZpVVFKeEFTejhYUFdpTDVoN1d4Y2lISjZZcmRkSTVsOEw1ZDQ5U2FLMjQ5ckNrTExxRUFIZW1nMndleXdSZ0ZDRTZNOXNtVzV6eWlnWDBiSyUyRkdad1hXWTZucElONUJQTCUyQlYyU1BFVGZlUWpQUWNaOFZVR2QlMkZTQnJtODNMb05oTHNoek1oZzJkYnZFWDdUZlhReUZlJTJGYzlNSGU0N1pqVkhNTGJiZnk3MkkyZ2dFVyUyRlclMkIlMkZoWG8lMkJBYmZWd2lUMmV1R2VvQkNqQktvSTVLRjFKeWQxWUhKcmFyMnNjMmJsMHF6dEtUJTJCOWEzU3Y2OG4lMkZFeHRpWENvR0ZBREtIVWIlMkJUczVhYUtVQzFMMCUyQlZCQkozaEREMEhjc1B4OUFhS3liNE0xTnV5RndNWldwTFVIeHllWmlNRm0xdjhZWkNNWGNPdE9UZTVKQ3RtJTJCSHN1NyUyRmVDY1JsdlBYZDJwWiZYLUFtei1TaWduYXR1cmU9NmUxNjRiNDZhYmYyN2EwMWFiNjJmNDY3NDU1YmJkMmRjNDQ0OWE2NTEwOWMxMjgwMzAxNDMxNGFmNmFkMDZhOSZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QmVmVyc2lvbj0x")
AWS_REGION   = "ap-southeast-2"
LLM_MODEL    = "amazon.nova-pro-v1:0"

os.environ["AWS_BEARER_TOKEN_BEDROCK"] = BEARER_TOKEN

# ── AWS client ────────────────────────────────────────────────────────────────
bedrock = boto3.client("bedrock-runtime", region_name=AWS_REGION)

# ── Load data ─────────────────────────────────────────────────────────────────
with open("synthetic_batch_records.json") as f:
    batch_records = json.load(f)

df_detection = pd.read_csv("batch_detection_results.csv")
df_reviews   = pd.read_csv("batch_review_summaries.csv")

# Parse the stringified list columns back into Python objects
df_detection["true_exceptions"] = df_detection["true_exceptions"].apply(eval)
df_detection["detected"]        = df_detection["detected"].apply(eval)
df_reviews["findings"]          = df_reviews["findings"].apply(eval)

# ── FastAPI ───────────────────────────────────────────────────────────────────
app       = FastAPI(title="UCB Batch Record Review Dashboard")
templates = Jinja2Templates(directory="br_templates")

SYSTEM_PROMPT = """You are a pharmaceutical quality assurance assistant.
Answer questions about batch record review findings, exception patterns,
and release decisions. Use the provided data context to give specific answers.
Keep responses concise — under 150 words."""


# ── Routes ────────────────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    total_batches   = len(batch_records)
    flagged_batches = len(df_reviews)
    clean_batches   = total_batches - flagged_batches

    # Severity breakdown
    all_findings = [f for findings in df_reviews["findings"] for f in findings]
    severity_counts = pd.Series([f["severity"] for f in all_findings]).value_counts().to_dict()

    # Exception type breakdown
    exception_counts = pd.Series([f["code"] for f in all_findings]).value_counts().to_dict()

    # Top flagged batches by number of findings
    top_batches = (
        df_reviews
        .sort_values("n_findings", ascending=False)
        .head(10)
        [["batch_id", "product", "n_findings"]]
        .to_dict("records")
    )

    # Product breakdown
    products = sorted(set(r["product"] for r in batch_records))

    return templates.TemplateResponse("br_dashboard.html", {
        "request"          : request,
        "total_batches"    : total_batches,
        "flagged_batches"  : flagged_batches,
        "clean_batches"    : clean_batches,
        "pass_rate"        : round(clean_batches / total_batches * 100, 1),
        "severity_counts"  : severity_counts,
        "exception_counts" : exception_counts,
        "top_batches"      : top_batches,
        "products"         : products,
    })


@app.get("/batches")
async def get_batches(product: str = None, status: str = None):
    flagged_ids = set(df_reviews["batch_id"])

    results = []
    for r in batch_records:
        if product and r["product"] != product:
            continue
        is_flagged = r["batch_id"] in flagged_ids
        if status == "flagged" and not is_flagged:
            continue
        if status == "clean" and is_flagged:
            continue

        results.append({
            "batch_id"  : r["batch_id"],
            "product"   : r["product"],
            "batch_date": r["batch_date"],
            "operator"  : r["operator"],
            "flagged"   : is_flagged,
        })

    return results[:50]


@app.get("/batch/{batch_id}")
async def get_batch_detail(batch_id: str):
    record = next((r for r in batch_records if r["batch_id"] == batch_id), None)
    if not record:
        return {"error": "Batch not found"}

    review = df_reviews[df_reviews["batch_id"] == batch_id]
    review_data = review.to_dict("records")[0] if len(review) > 0 else None

    return {
        "record": record,
        "review": review_data,
    }


@app.post("/chat")
async def chat(request: Request):
    body     = await request.json()
    question = body.get("question", "").strip()

    if not question:
        return {"error": "No question provided."}

    all_findings    = [f for findings in df_reviews["findings"] for f in findings]
    severity_counts = pd.Series([f["severity"] for f in all_findings]).value_counts()
    exception_counts= pd.Series([f["code"] for f in all_findings]).value_counts()

    # Check if the question mentions a specific batch ID — give full detail if so
    mentioned_batch = None
    for r in batch_records:
        if r["batch_id"].lower() in question.lower():
            mentioned_batch = r
            break

    batch_detail_context = ""
    if mentioned_batch:
        review = df_reviews[df_reviews["batch_id"] == mentioned_batch["batch_id"]]
        review_summary = review.to_dict("records")[0]["summary"] if len(review) > 0 else "No exceptions found — batch passed clean."
        batch_detail_context = f"""

Full record for {mentioned_batch['batch_id']}:
{json.dumps(mentioned_batch, indent=2)}

Review summary for this batch:
{review_summary}
"""

    # Always include a compact list of all flagged batches so the LLM can
    # answer questions referencing any batch, product, or operator
    flagged_batch_list = df_reviews[["batch_id", "product", "n_findings"]].to_string(index=False)
    all_batch_list = pd.DataFrame(batch_records)[["batch_id", "product", "batch_date", "operator", "qa_reviewer"]].to_string(index=False)

    context = f"""
Batch record review data:

Total batches reviewed: {len(batch_records)}
Batches flagged for review: {len(df_reviews)}
Batches passed clean: {len(batch_records) - len(df_reviews)}

Severity breakdown:
{severity_counts.to_string()}

Exception type breakdown:
{exception_counts.to_string()}

All flagged batches:
{flagged_batch_list}

All batches (id, product, date, operator, QA reviewer):
{all_batch_list}
{batch_detail_context}
"""

    prompt = f"""{context}

Question: {question}"""

    try:
        response = bedrock.converse(
            modelId=LLM_MODEL,
            system=[{"text": SYSTEM_PROMPT}],
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={"maxTokens": 400, "temperature": 0}
        )
        answer = response["output"]["message"]["content"][0]["text"]
        return {"answer": answer}
    except Exception as e:
        return {"error": str(e)}


@app.get("/health")
async def health():
    return {
        "status"        : "ok",
        "total_batches" : len(batch_records),
        "flagged"       : len(df_reviews),
        "model"         : LLM_MODEL,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("br_app:app", host="0.0.0.0", port=8002, reload=True)