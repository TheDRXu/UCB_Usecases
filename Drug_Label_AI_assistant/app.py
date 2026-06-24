import json
import os
import time
import boto3
import chromadb
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates

# ── Config ──────────────────────────────────────────────────────────────────
BEARER_TOKEN  = os.environ.get("AWS_BEARER_TOKEN_BEDROCK", "bedrock-api-key-YmVkcm9jay5hbWF6b25hd3MuY29tLz9BY3Rpb249Q2FsbFdpdGhCZWFyZXJUb2tlbiZYLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFTSUE0WDZWRFZOWUs2VEZTM0NZJTJGMjAyNjA2MjMlMkZhcC1zb3V0aGVhc3QtMiUyRmJlZHJvY2slMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI2MDYyM1QwNjMyMzdaJlgtQW16LUV4cGlyZXM9NDMyMDAmWC1BbXotU2VjdXJpdHktVG9rZW49SVFvSmIzSnBaMmx1WDJWakVFOGFEbUZ3TFhOdmRYUm9aV0Z6ZEMweUlrWXdSQUlnSXZId3JVdE52d1d5M0hoUll5YVhCb3hZUXRYTTkxOVZhVTJ1dW8lMkJVRkxZQ0lBNHoySmF4VElHbk54UVpscDNGRUhkN0ZSejQ4RFAxV0lqNXczN0hJUnRhS29jRkNCZ1FBQm9NT0RjMk1EZ3pNemt4TXpRMElneFI5T3JZaDB1SGdKTlN6VHNxNUFTM21TQWxtVlZncjByVGtySk0lMkZSZEkwQ2FET2dwUjA4VGFjaDQ0ZGpkN2xGQWpNUXlQdWJ2TDRmWUkyQk0xbkg2bCUyQkJOQ05iNEVycnl0bEZRV2dtUUVGTzlEd211UGhvenljS09hbEJ0eXUwYUN0SWlYbWcyMFhjOHVUNm92SDdlOUpvVjhGYkRraVclMkJuVkVSelIyaEVYVlduRU9aeEhBUXZ3cEE3Z2lSbFRGenVvY04zJTJGJTJCJTJGTERTODdERU5TeFJxdUhSUHdiMEdjYnFrYmJ3bjQ0Y3ZDNDVTeVZOQjAzVDZRSkJxelFSSkVJV3h1Um45MFk5MGRVZUtjcU4yZzlpM0xzZ3VNZDZQVXBXbmtmQ2phUklkajhyZ29YJTJGb2NsTHlKYXBXSWNBQU4zRDZsRkxmUTg2a01KREIwRGZvYlVnQ1VaZEtGcTVSamFVVjFSa09UbEJDZ25zSnpnQVVJZ1FESWROODNzMVpJRjVmdHdRNkFkYUhZVllGZ3FYVHp0S2c5QzNxRERWNDBBbW5NOU5SJTJCYmRhYnJ6SDcyd01VUjhuMDk1Rk9vOXZPOHhaM1EzOUp4MEZIMGFiRWczOXQ0SGNYMnFzNUdNckowOWFocVMyNDclMkZ0aEN0M1FqcEFiajZ4N2hyaEpvTGhPb2QwTiUyRmoyTmpvUmhFJTJCcTJLZGdpRlhvJTJGZG1jTlpFWUtXMzZtMk5QbW9qSVVBQnVLNlpOVWhUNTI0WUREZ1JpNEh1SlJEcW5NTThIVnBOUyUyQnBnRW9uSmpPMyUyQm9waXJBQW02MjlVdk5ER0NZYTdMJTJGZnU1bkVxVTUwbVhoT2hjbTN3MmJjU3Z0OUduUkdkYVozeHR0b0dDSFFET1M4Y2h4WEtOUnV3aVR6N0V4JTJGcFNyMXA1ViUyQlpqWHhEekF5bncwWk1MbElDdWJ6ZmcweFZPalA5NGRDY2xHQ29GMGtDR0pSNWQzdlI4N1BWR3EwWkduQ2FoNUdjRUFqbHk2anNhTzBRYVFMWnI4RUo0YlBvdlQwZFAzVzYxZ3pueFRZUmpidW9VSkVtcmclMkJacmdpUkZ4c2tsak1DYjZobDBtejJvbXJMUEtoOWwwdzlORG8wUVk2eUFKR1FrVDBhOU50ZFN2WFFlazdFJTJCUjg0Z0c5VU8waWJjNlFORVVSRndVcyUyRmkwamVPQ3FKT054dnBodDVrajlGcFZvSzFKQ3gzcDBhVWJQS3pnbndxdk01Qk41dXNCb2RiQVRkJTJGYWsxUyUyQjRHc1VwSElZa1NHNlB5bm9KSUdSRUtFYVZZQkZwNU9Kb0F3MHFzeHpZJTJCaVBEVllmVlE4emJrRkNEQ0JhemZDNUJ4RUgzRFRHRnZzUzVnNWo1Vnl4eGZhRE85R0JBczUwaCUyQjA4Z29pdGRnanIzZnFTbjByUEg3YjNIZmF5a3JOWXpIQVRQbzB3b2x5Z21HaDVDRkFMJTJCWVAyOVRsWnJpT0U2YUp3NDA3b2tscjY0SVJOMVlRWnAxUjdYd2dkalolMkJxTVc2VnVQYWdueWJBRiUyQjY4bjBHYWpicW40R0hDS00yZUp3JTJGclQzcDZDYlpuTlAzckh2Rk1SRER5cDdzcyUyRm1ycFhFNEVGUUlzZ3BNNWFEWEp5WVAxZjNhUDNQeDhPNU1zazFEeHBEJTJCRjlCSXFZMWZFV3gwNUhGWTlITjVnc1NUQzlvbFJKUFVrZWFPY0UmWC1BbXotU2lnbmF0dXJlPTgzMWJlMDU2MWMxZWY0ODJkMDMzMTMwODE2MzczYzEyNDM1MzVmNjJmNGNiMzkzYzU4NTcxY2UyODM3NGMyMzUmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0JlZlcnNpb249MQ==")
AWS_REGION    = "ap-southeast-2"
EMBED_MODEL   = "amazon.titan-embed-text-v2:0"
LLM_MODEL     = "amazon.nova-pro-v1:0"
CHROMA_PATH   = "./chroma_db_bedrock"
CHUNKS_FILE   = "./all_drugs_chunks.json"
MAX_CHARS     = 6000
N_RESULTS     = 5

os.environ["AWS_BEARER_TOKEN_BEDROCK"] = BEARER_TOKEN

# ── AWS clients ──────────────────────────────────────────────────────────────
bedrock      = boto3.client("bedrock-runtime", region_name=AWS_REGION)
embed_client = boto3.client("bedrock-runtime", region_name=AWS_REGION)

# ── ChromaDB ─────────────────────────────────────────────────────────────────
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection    = chroma_client.get_collection("fda_labels_bedrock")

# ── FastAPI ───────────────────────────────────────────────────────────────────
app       = FastAPI(title="FDA Drug Label RAG Assistant")
templates = Jinja2Templates(directory="templates")

SYSTEM_PROMPT = """You are a pharmaceutical regulatory assistant at UCB.
Answer questions using ONLY the provided FDA label sections.
Do not use any external knowledge or make anything up.
Always end your answer with a citation in this exact format:
Source: [drug name] — [section name]"""


# ── Core functions ────────────────────────────────────────────────────────────
def embed_text(text: str) -> list:
    if len(text) > MAX_CHARS:
        text = text[:MAX_CHARS]
    body = json.dumps({
        "inputText": text,
        "dimensions": 256,
        "normalize": True
    })
    response = embed_client.invoke_model(
        modelId=EMBED_MODEL,
        body=body,
        contentType="application/json",
        accept="application/json"
    )
    return json.loads(response["body"].read())["embedding"]


def retrieve(question: str) -> dict:
    query_embedding = embed_text(question)
    return collection.query(
        query_embeddings=[query_embedding],
        n_results=N_RESULTS
    )


def build_prompt(question: str, results: dict) -> str:
    context_blocks = []
    for i, (doc, meta) in enumerate(zip(
        results["documents"][0],
        results["metadatas"][0]
    )):
        context_blocks.append(
            f"[Source {i+1}]\n"
            f"Drug: {meta['drug']}\n"
            f"Section: {meta['section']}\n"
            f"Subsection: {meta['subsection']}\n"
            f"Text: {doc}\n"
        )
    context = "\n\n".join(context_blocks)
    return f"""--- FDA LABEL SECTIONS ---
{context}

--- QUESTION ---
{question}"""


def ask(question: str) -> dict:
    start     = time.time()
    results   = retrieve(question)
    prompt    = build_prompt(question, results)

    response  = bedrock.converse(
        modelId=LLM_MODEL,
        system=[{"text": SYSTEM_PROMPT}],
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig={"maxTokens": 1024, "temperature": 0}
    )

    answer    = response["output"]["message"]["content"][0]["text"]
    elapsed   = round(time.time() - start, 2)
    drugs_hit = list(set([m["drug"] for m in results["metadatas"][0]]))
    top_score = round(1 - min(results["distances"][0]), 3)

    return {
        "answer"   : answer,
        "elapsed"  : elapsed,
        "drugs_hit": drugs_hit,
        "top_score": top_score,
    }


# ── Routes ────────────────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/chat")
async def chat(request: Request):
    body     = await request.json()
    question = body.get("question", "").strip()

    if not question:
        return {"error": "No question provided."}

    try:
        result = ask(question)
        return result
    except Exception as e:
        return {"error": str(e)}


@app.get("/health")
async def health():
    return {
        "status"      : "ok",
        "chunks"      : collection.count(),
        "model"       : LLM_MODEL,
        "embed_model" : EMBED_MODEL,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)