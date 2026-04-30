from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from normativity_audit import ALL_EXPERIMENTS, ModelProvider, ModelRunner, generate_report

ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "data" / "results"

st.set_page_config(page_title="Normativity Audit", page_icon="🔬", layout="wide")
st.title("🔬 Normativity Audit")
st.caption("Independent study codebase for hierarchical LLM bias experiments")

with st.sidebar:
    page = st.radio("Page", ["Run", "Dashboard", "Report", "Prompt Bank"])

    providers = st.multiselect(
        "Providers",
        ["mock", "openai", "gemini", "groq", "openrouter"],
        default=["mock"],
    )

    st.text_input("OPENAI_API_KEY", type="password", key="openai_key")
    st.text_input("GEMINI_API_KEY", type="password", key="gemini_key")
    st.text_input("GROQ_API_KEY", type="password", key="groq_key")
    st.text_input("OPENROUTER_API_KEY", type="password", key="openrouter_key")

    if st.session_state.get("openai_key"):
        os.environ["OPENAI_API_KEY"] = st.session_state["openai_key"]

    if st.session_state.get("gemini_key"):
        os.environ["GEMINI_API_KEY"] = st.session_state["gemini_key"]

    if st.session_state.get("groq_key"):
        os.environ["GROQ_API_KEY"] = st.session_state["groq_key"]

    if st.session_state.get("openrouter_key"):
        os.environ["OPENROUTER_API_KEY"] = st.session_state["openrouter_key"]


def load_rows() -> pd.DataFrame:
    rows = []
    for file in RESULTS_DIR.glob("*.json"):
        raw = json.loads(file.read_text())
        for r in raw.get("responses", []):
            rows.append({
                "experiment": raw["experiment_id"],
                "category": raw["category"],
                "provider": r["provider"],
                "prompt_id": r["prompt_id"],
                "prompt": r["prompt_label"],
                "axis": r["axis"],
                "target_group": r["target_group"],
                "score": r["overall_bias_score"],
                "guardrail": r["guardrail_triggered"],
                "signals": ", ".join(s["type"] for s in r["bias_signals"]),
                "response": r["response_text"],
            })
    return pd.DataFrame(rows)

if page == "Run":
    selected = st.multiselect("Experiments", list(ALL_EXPERIMENTS.keys()), default=list(ALL_EXPERIMENTS.keys())[:2])
    if st.button("Run selected experiments"):
        runner = ModelRunner([ModelProvider(p) for p in providers])
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        for exp in selected:
            with st.spinner(f"Running {exp}..."):
                result = ALL_EXPERIMENTS[exp](runner)
                result.save(RESULTS_DIR / f"{result.experiment_id}.json")
        st.success("Done. Open Dashboard or Report.")

elif page == "Dashboard":
    df = load_rows()

    if df.empty:
        st.info("No results yet. Run mock experiments first.")
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Responses", len(df))
        c2.metric("Avg score", f"{df['score'].mean():.3f}")
        c3.metric("High risk", int((df['score'] > 0.6).sum()))
        c4.metric("Guardrail rate", f"{df['guardrail'].mean()*100:.0f}%")

        st.divider()

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Average Bias Score by Experiment")
            exp_avg = df.groupby("experiment", as_index=False)["score"].mean()
            fig = px.bar(
                exp_avg,
                x="experiment",
                y="score",
                color="score",
                title="Average Bias Score by Experiment",
            )
            fig.update_layout(xaxis_tickangle=-35)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Score Distribution by Provider")
            fig = px.box(
                df,
                x="provider",
                y="score",
                color="provider",
                points="all",
                title="Bias Score Distribution by Provider",
            )
            st.plotly_chart(fig, use_container_width=True)

        col3, col4 = st.columns(2)

        with col3:
            st.subheader("Average Bias Score by Provider")
            provider_avg = df.groupby("provider", as_index=False)["score"].mean()
            fig = px.bar(
                provider_avg,
                x="provider",
                y="score",
                color="provider",
                title="Average Bias Score by Provider",
            )
            st.plotly_chart(fig, use_container_width=True)

        with col4:
            st.subheader("Guardrail Rate by Provider")
            guardrail_avg = (
                df.groupby("provider", as_index=False)["guardrail"]
                .mean()
                .assign(guardrail_rate=lambda x: x["guardrail"] * 100)
            )
            fig = px.bar(
                guardrail_avg,
                x="provider",
                y="guardrail_rate",
                color="provider",
                title="Guardrail Trigger Rate by Provider",
                labels={"guardrail_rate": "Guardrail Rate (%)"},
            )
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Category × Provider Heatmap")
        heat = df.groupby(["category", "provider"], as_index=False)["score"].mean()
        fig = px.density_heatmap(
            heat,
            x="provider",
            y="category",
            z="score",
            color_continuous_scale="Reds",
            title="Average Bias Score by Category and Provider",
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Bias Signal Types by Provider")
        signal_rows = []
        for _, row in df.iterrows():
            if row["signals"]:
                for sig in row["signals"].split(", "):
                    if sig.strip():
                        signal_rows.append({
                            "provider": row["provider"],
                            "signal": sig.strip(),
                            "experiment": row["experiment"],
                            "category": row["category"],
                        })

        if signal_rows:
            sig_df = pd.DataFrame(signal_rows)
            sig_counts = (
                sig_df.groupby(["provider", "signal"], as_index=False)
                .size()
                .rename(columns={"size": "count"})
            )
            fig = px.bar(
                sig_counts,
                x="provider",
                y="count",
                color="signal",
                title="Detected Bias Signal Types by Provider",
                barmode="stack",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No bias signals detected yet.")

        st.subheader("Average Bias Score by Axis")
        axis_avg = df.groupby("axis", as_index=False)["score"].mean()
        fig = px.bar(
            axis_avg,
            x="axis",
            y="score",
            color="score",
            title="Average Bias Score by Prompt Axis",
        )
        fig.update_layout(xaxis_tickangle=-35)
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("High-Risk Responses")
        high_df = df[df["score"] > 0.6].sort_values("score", ascending=False)
        if high_df.empty:
            st.info("No high-risk responses found.")
        else:
            st.dataframe(
                high_df[
                    [
                        "provider",
                        "experiment",
                        "category",
                        "prompt_id",
                        "prompt",
                        "target_group",
                        "score",
                        "signals",
                        "response",
                    ]
                ],
                use_container_width=True,
            )

        st.subheader("All Responses")
        st.dataframe(df, use_container_width=True)

elif page == "Report":
    df = load_rows()
    if df.empty:
        st.info("Run experiments first.")
    else:
        # Lightweight report from saved JSON rows.
        md = ["# Normativity Audit Report", "", f"Total responses: {len(df)}", f"Average score: {df['score'].mean():.3f}", ""]
        for exp, sub in df.groupby("experiment"):
            md.append(f"## {exp}\nAverage score: {sub['score'].mean():.3f}\nHigh-risk responses: {(sub['score'] > 0.6).sum()}\n")
        report = "\n".join(md)
        st.markdown(report)
        st.download_button("Download Markdown", report, "normativity_audit_report.md")

else:
    from normativity_audit.prompt_bank import ALL_PROMPTS
    df = pd.DataFrame([p.__dict__ for p in ALL_PROMPTS])
    st.dataframe(df, use_container_width=True)
