import json
import os
import boto3
import pandas as pd
import numpy as np
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# ── Config ───────────────────────────────────────────────────────────────────
BEARER_TOKEN = os.environ.get("AWS_BEARER_TOKEN_BEDROCK", "bedrock-api-key-YmVkcm9jay5hbWF6b25hd3MuY29tLz9BY3Rpb249Q2FsbFdpdGhCZWFyZXJUb2tlbiZYLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFTSUE0WDZWRFZOWUxDT1NSSENLJTJGMjAyNjA2MjQlMkZhcC1zb3V0aGVhc3QtMiUyRmJlZHJvY2slMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI2MDYyNFQwNzU0NTJaJlgtQW16LUV4cGlyZXM9NDMyMDAmWC1BbXotU2VjdXJpdHktVG9rZW49SVFvSmIzSnBaMmx1WDJWakVHZ2FEbUZ3TFhOdmRYUm9aV0Z6ZEMweUlrWXdSQUlnU3JLTFZZRGFyOXc3RE5ncWRXZjlDaW0lMkJEWENGVUg5SWhsVXFaVjhLcTJRQ0lGUFdhN3QzSGRVbUpRbXowU1dFMTd3Y3FoR1BwVTFNZ0E0QTB1MUklMkI5ZDlLb2NGQ0RFUUFCb01PRGMyTURnek16a3hNelEwSWd3MDVpZG9QRG1FRlc5eHA3MHE1QVQ5dWFqSG1Jd1d5WGxTdHpwbjlhcjNoWmZrazNZR0tzQVcwUnEzSkNLT0laamVvWHoxTWUwVHJGVFA0ODNUUEthUVR4MjJ3SUJsUm5Ub1JnY1RGRldETmYzTkVVdVlJRlg2S3YzaXdmVkNoZWdJRjhmOFl3OElnTnhUYnpFUkpuZDJLcjREeXBLRG5xSDZodVZNR0klMkYyb0RscEo5d1pvU1dqSWhrQURlY2xtTmklMkJkQnglMkJpOHVFYzdUcWZlMUxoM2ZvdmF2WVN6aEhLVUVJcWpvUXExTlZOa3dhdUpnUXV6OWczbUdjNmYyTEk4eSUyQiUyQlJXRTRLQk9hZ2VGaiUyQnJ5dEhzV3VNTGglMkJoVlp1b3I1aW1nUWF1dmRGWmhMbENuJTJCQW44UXVXUmkyMEQlMkJaTGZrMHFRdTd1dTJ5cDZIRUhMaWJSbyUyQm10dnZHSEJCVjFQTzdhMmt2YiUyQmRCMUd2TE4lMkY1dTVack94QmpTYnRoJTJGWFdDN0luJTJGS2NiJTJGQmRjN0xJSm9OZmFYN2RSdGtlbWJSTEU0NlJ1azhHY3clMkJRenllM2ZmRlU5V1hiYm1LTFJtaUhqTHhtNTlRWm0yaGthcnZHaWFqYkk1JTJGaGlvYUNxUjBZNTBZUE83ZXFqakxxNllhdGt1enBVS09ydm1YViUyRkpOWkQ0ck9PZWxOSlFQMlFLalp0MGhveWM2YzQ4VDZSTCUyQnlEcW5yaWFPaXclMkJzaGhqcUtYc0NrNUlZTGM0TTg2d1JYNThDM0xSeDNJVjVPR0tEbDNNeW5Pem1TUDdGZ1NmUnFKUUVFbHJzdnJIeEN5SEJFNWZGS3pLVHR4blZ5dDJ1SEVYdlh0Q0RnR1d6MVRLQkhiVDZ0Q2NOc1lUNjRnNlRYNiUyQm4xZHNaaWhEN1NoNjJZVDNYbjhqV3M4c1djaElIV0lBRk1Ca3NOJTJCOTdzM0xiYzNtd3c2NnE2U3B1ZWlyeDlKOFIzTklEbFd5JTJGcGdWOU9NOWpmUmE3UWslMkZ4S0JmQnJzQ3V2aTh6d1FDS1p0QVkzVWJEVXk4b0xNZ3BaS0Z3VHhqN1hmJTJGWXQ5WVBBb1A1VjREbCUyQjlMeE8zdFFRT1p5USUyQmM3cVF3cjVydTBRWTZ5QUpOdTFDWGxyTUtkcW9RMDBJb2JON3QzcDN4eFY3ZFg0aTFxV2M2a3U0TnNWaVJyTXluVGk5TUFqUVZzRiUyQnpBRXRFenRxT1Vkek5GQVdmNFZsblhTMXo2JTJGUXNZYm1uYjRXeTVJQSUyQkpZREslMkZTOWNnZFdGVGVHemswS1k1NHdxMnU2SFhZVnJMQ0Y1cHhueTh1R09nSDE0bWs5N1ZpT21FaE9nY29UWEprWHViSWRzQ2FDJTJCVWNERG1wVldGVFJkcFhjd2Vhalo5VExtY1JwQ1JKMVdaelBmJTJGR0lXeENWNXR5TyUyRkpjOWprMDVtYTlPWm9EcVolMkZCU3RYTzNmYVU4Rm14NWpxSXdiaWI2SEclMkZZMEhYSXJFVG5sVGVQQmZmN3BhbmNVanBPa09hdEFzVGRPY2Z6SGhXZFQ0N1RtbUhqbWFUT0JEdWVlZU90S05yNngxUUdsOXMlMkJzd09CekYlMkZvSEM0UG5GZ1hzR01qSDZFWEpwMmdxNHQlMkZJSEIlMkZCaEdkZmlHTGNuV3JMcE94a1hnaTdVZVZzYTQ2NjdPNW1DaHhrMVF5STUwUiUyQjRIZUh3aFhEaUExUlB1YlQmWC1BbXotU2lnbmF0dXJlPTBiOTJmNTI0ZDI5MDRiYWZjMDU0YTg2ZGVjMWE4NjRhNDViYjkwYjAxNDM1OWQ1ODJhZDQ4MWU0ZWRkNzEyZWEmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0JlZlcnNpb249MQ==")
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
