import json
import os
import boto3
import pandas as pd
import numpy as np
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# ── Config ───────────────────────────────────────────────────────────────────
BEARER_TOKEN = os.environ.get("AWS_BEARER_TOKEN_BEDROCK", "bedrock-api-key-YmVkcm9jay5hbWF6b25hd3MuY29tLz9BY3Rpb249Q2FsbFdpdGhCZWFyZXJUb2tlbiZYLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFTSUE0WDZWRFZOWU5OSE9aUFhLJTJGMjAyNjA2MjQlMkZhcC1zb3V0aGVhc3QtMiUyRmJlZHJvY2slMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI2MDYyNFQwNjQ1NTJaJlgtQW16LUV4cGlyZXM9NDMyMDAmWC1BbXotU2VjdXJpdHktVG9rZW49SVFvSmIzSnBaMmx1WDJWakVHY2FEbUZ3TFhOdmRYUm9aV0Z6ZEMweUlrWXdSQUlnTjR4b3ZCVjdmNXRrRzBwOVNjRmJMdEhBYlNhUXJ6RHpJVGhEU1NqZHRtMENJSDBpcXJqTVdHYXFLNGNkMGgwNUw1eUlkb0J6VXdIcUs3TG9DOFMyJTJCbHk2S29jRkNEQVFBQm9NT0RjMk1EZ3pNemt4TXpRMElndzZvSlZ1b21ZY3VYVmJIQzRxNUFRRkpKU3RqNktZMnVvY2ZYTFEzdnR3NUF4QUtxakMzTDlRQmFUNSUyQlZVU2NPaTVhMDZwVUVmJTJCWFdHMVdIYzNMd01IZXJzZW1RUWk4JTJGM1FTOHBkMzNJMHVTY0dXUE9rVUVLJTJCMGJOYXRCa0QxVHlJTWE1QmVLUG1pekE0ZzNxUHJsa3Fmd2pZTElXVFUlMkYwckVhQ3JuWGFYZUZaenYlMkJzUjNWbkhub0xQMkRTT3ZxRDN4SXAyMURBJTJGMVp1a1llTGpIQ01scTkwS1ZoODlFNDFaN1Rub3BGdzdXbHJiUG9OUmdwVFlpamJNMEwxbkE3czdYRU9CTVVTZ3o5c3hYTTM0YSUyRk8lMkJqcnRIeTJkbXQwUFVtZWZYWGd4ZXM3WnQ4V0lXaTBGbXdLN0lndUklMkJ0RkVUbkE5MnhwWGsyVGNyamNqZHl3a3dzVVRvVk1uclpEc3Zwcm5aZlRTdkJGSVJzcklYUFdNU1ZoMDIlMkJNRUYlMkJFZTdsSzkzZ2FZZGNEbzRRRzJ1bzhiTjJEcThsZ0tHbUpvRzlsVGZkWUw2U2ljOXoyMldWMk1VcGcxMEYxcUY2Znp4Nmo2VXJFWWRqZU5nUmpHQ1Bhb0xSJTJGV1B4a0EyU214aFZJQ2hTOG1uMHZuTmhRN3FVRXk2MkpRTEVTdm5XNUtJcWNNdEZJRm1YeU9aTHZ3QVklMkZDOHBoR0VkcUVnWUQlMkJHQ2Q2QnFKbUM1VlBLdGU5VGJkeE91RENwOXlZZ1J6dU1Nb0d4M1luTHpKdzdPbnJKcVYzSFMzVkdtenNkTDBvS25sWmRVbldsNmQyNW4yRE5SUmxlWHY2NnhRNVdva1pINUclMkZCJTJGcDFZZk1JekdwYTd0MkF4RUNmY1lmQnFadSUyQjRTWWlIdkZLUHY0VnZUY0NLU0glMkZER0xpZ1ZXMllWWWpBbFBpcXhzalpqVlp2cjMlMkJtamliUEpxUnlMTmJFOHRsJTJCWjJKNW40TWtqJTJCWnJPZWdkTlRIUjh5eXN4b3FsTnNOeEZtYTBPVFJ2SnhBVnQlMkZnUGQwZVhDcHd6dXI2JTJCbXBNODc5eCUyQkQya3lpV1VybTk4Q3VURGI5Sng3TFBva1J1M3pXeXd3aXZydDBRWTZ5QUlCSzc3V3B1a0h1TUhrcmdBUFJOQkRYckEwbWh6MFFkRUdaJTJGenkxMlZOQVFrNVNQOUlLUVk5Z2llb1ZJUnZkTnpuYTI3ZSUyQnlDcmxBTUl0WFVqbUdMcUd2dDBOb1ZKeE9VT2I2byUyQlhwQVJaZ2dxbXdmMTBkWCUyQkdxUG9reWpwZiUyQnVmbzRzd1V3ZnZsZUFJZ3FFbm4xTWNJRVU1MkF5QmtQU1dCZDVqYzE2eXhtSGFGUFFBQ1pKcFZMRDlVZGFDNzdrbHhxZmVkdWo5S3hLMHJHREdLSElOdWZqWU1ZJTJGN2R5MVJaJTJCU0hwNXBteUg1b1gzTWVLdVJkY1JIZ3FibGhJamFxeiUyQiUyQndKR25ISkFoU1lpSHk3SjZDeTd6NDJ3bEx4OXpZeU11ZjdOYktlc2VUcG1Pd2g5T0slMkJFd1pHVEd4RjFtTkt2VDhFd2slMkZ1Z01BaDZYeTJ3czdld2Z6N2ZmaTRMMGI4N2lLMEVsYTc5dmR1c0pGVXhTZmpWaWNyZiUyRkQlMkJvTFN1QlVuY3dOdjBVJTJGeEpxNDFUN2h3SVFIJTJGakVHVlJiZWl4dU9yTHg2UHpINmlPTDFXbGJVSSZYLUFtei1TaWduYXR1cmU9YmVjNTAzYTljMTg4Yjg1ZTFmNmEyODlhNjM5MzkxN2I4ODIyNTA1NTBmNTg3OTkwZDdlYTIwNzM4NzVjNzlmMiZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QmVmVyc2lvbj0x")
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
