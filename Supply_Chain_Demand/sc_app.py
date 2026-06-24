import json
import os
import boto3
import pandas as pd
import numpy as np
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# ── Config ───────────────────────────────────────────────────────────────────
BEARER_TOKEN = os.environ.get("AWS_BEARER_TOKEN_BEDROCK", "")
AWS_REGION   = "ap-southeast-2"
LLM_MODEL    = "amazon.nova-pro-v1:0"

os.environ["AWS_BEARER_TOKEN_BEDROCK"] = BEARER_TOKEN

# ── AWS client ────────────────────────────────────────────────────────────────
bedrock = boto3.client("bedrock-runtime", region_name=AWS_REGION)

# ── Load data ─────────────────────────────────────────────────────────────────
df_alerts  = pd.read_csv("supply_chain_alerts_all_drugs.csv")
df_demand  = pd.read_csv("aed_demand_by_state.csv")
df_national = pd.read_csv("aed_demand_national.csv")

# ── FastAPI ───────────────────────────────────────────────────────────────────
app       = FastAPI(title="UCB Supply Chain Dashboard")
templates = Jinja2Templates(directory="sc_templates")

SYSTEM_PROMPT = """You are a supply chain intelligence assistant at UCB Pharmaceuticals.
Answer questions about AED drug demand, supply chain anomalies, and inventory recommendations.
Use the provided data context to give specific, actionable answers.
Keep responses concise — under 150 words."""


# ── Routes ────────────────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    # Summary stats for dashboard
    total_alerts = len(df_alerts)
    spike_alerts = len(df_alerts[df_alerts["flag_type"] == "SPIKE"])
    drop_alerts  = len(df_alerts[df_alerts["flag_type"] == "DROP"])
    drugs        = sorted(df_alerts["drug"].unique().tolist())
    states       = sorted(df_alerts["state"].unique().tolist())

    # Top alerts by deviation
    top_alerts = (
        df_alerts
        .assign(abs_dev=df_alerts["deviation"].abs())
        .nlargest(5, "abs_dev")
        [["drug", "state", "date", "flag_type", "deviation", "actual", "forecast"]]
        .to_dict("records")
    )

    # National demand summary
    national = df_national[["drug", "total_claims"]].to_dict("records")

    return templates.TemplateResponse("sc_dashboard.html", {
        "request"      : request,
        "total_alerts" : total_alerts,
        "spike_alerts" : spike_alerts,
        "drop_alerts"  : drop_alerts,
        "drugs"        : drugs,
        "states"       : states,
        "top_alerts"   : top_alerts,
        "national"     : national,
    })


@app.get("/alerts")
async def get_alerts(drug: str = None, state: str = None, flag_type: str = None):
    df = df_alerts.copy()
    if drug:
        df = df[df["drug"] == drug]
    if state:
        df = df[df["state"] == state]
    if flag_type:
        df = df[df["flag_type"] == flag_type]
    return df[["drug", "state", "date", "flag_type",
               "deviation", "actual", "forecast", "alert"]].to_dict("records")


@app.get("/demand")
async def get_demand(drug: str = None):
    df = df_demand.copy()
    if drug:
        df = df[df["drug"] == drug]
    top = (
        df.groupby(["drug", "state"])["total_claims"]
        .sum()
        .reset_index()
        .sort_values("total_claims", ascending=False)
        .head(20)
    )
    return top.to_dict("records")


@app.post("/chat")
async def chat(request: Request):
    body     = await request.json()
    question = body.get("question", "").strip()

    if not question:
        return {"error": "No question provided."}

    # Build context from data
    alert_summary = df_alerts.groupby(["drug", "flag_type"]).size().reset_index(name="count")
    top_demand    = df_national.nlargest(5, "total_claims")[["drug", "total_claims"]]

    context = f"""
Current supply chain data:

Total anomalies detected: {len(df_alerts)}
Spike alerts: {len(df_alerts[df_alerts['flag_type']=='SPIKE'])}
Drop alerts: {len(df_alerts[df_alerts['flag_type']=='DROP'])}

Alert breakdown by drug:
{alert_summary.to_string(index=False)}

Top 5 drugs by national demand (2024 Medicare Part D):
{top_demand.to_string(index=False)}

Recent high-priority alerts:
{df_alerts.nlargest(3, 'deviation')[['drug','state','date','flag_type','deviation','alert']].to_string(index=False)}
"""

    prompt = f"""{context}

Question: {question}"""

    try:
        response = bedrock.converse(
            modelId=LLM_MODEL,
            system=[{"text": SYSTEM_PROMPT}],
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={"maxTokens": 300, "temperature": 0}
        )
        answer = response["output"]["message"]["content"][0]["text"]
        return {"answer": answer}
    except Exception as e:
        return {"error": str(e)}


@app.get("/health")
async def health():
    return {
        "status"       : "ok",
        "total_alerts" : len(df_alerts),
        "drugs"        : df_alerts["drug"].nunique(),
        "model"        : LLM_MODEL,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("sc_app:app", host="0.0.0.0", port=8001, reload=True)
