"""Streamlit executive / engineering dashboard."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.telemetry.metrics import MetricsCalculator
from app.telemetry.repository import TelemetryRepository

st.set_page_config(
    page_title="Enterprise AI Engineering Dashboard",
    page_icon="📊",
    layout="wide",
)

st.title("Enterprise AI Engineering Dashboard")
st.caption(
    "Simulated and local telemetry for governed agentic engineering workflows. "
    "Productivity figures are labeled estimates, not experimentally validated results."
)

repo = TelemetryRepository()
metrics = MetricsCalculator(repo).summarize()
tasks = repo.list_tasks(limit=50)

delivery = metrics["delivery"]
ai = metrics["ai"]
governance = metrics["governance"]
productivity = metrics["productivity"]
outcomes = metrics["outcomes"]

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Tasks Completed", delivery["tasks_completed"])
c2.metric("AI Success Rate", f"{ai['plan_success_rate']}%")
c3.metric("Test Pass Rate", f"{delivery['test_pass_rate']}%")
c4.metric("Policy Blocks", governance["prevented_critical_actions"])
c5.metric("Human Approvals", governance["approvals_granted"])
c6.metric("Est. Hours Saved", productivity["estimated_hours_saved"])

st.info(
    f"Productivity model label: **{productivity['label']}** — "
    f"{productivity['estimated_minutes_saved']} estimated minutes saved "
    f"({productivity['productivity_gain_percent']}% gain)."
)

left, right = st.columns(2)

if tasks:
    df = pd.DataFrame(tasks)
    df["created_at"] = pd.to_datetime(df["created_at"], utc=True, errors="coerce")
    df["day"] = df["created_at"].dt.date

    with left:
        daily = df.groupby("day").size().reset_index(name="tasks")
        fig = px.line(daily, x="day", y="tasks", title="Tasks Over Time")
        st.plotly_chart(fig, use_container_width=True)

        outcome_df = pd.DataFrame(
            {"outcome": list(outcomes.keys()), "count": list(outcomes.values())}
        )
        fig2 = px.pie(outcome_df, names="outcome", values="count", title="Task Outcomes")
        st.plotly_chart(fig2, use_container_width=True)

        risk_counts = (
            df["risk_level"].fillna("unknown").value_counts().reset_index()
            if "risk_level" in df.columns
            else pd.DataFrame({"risk_level": [], "count": []})
        )
        risk_counts.columns = ["risk_level", "count"]
        fig3 = px.bar(risk_counts, x="risk_level", y="count", title="Risk Distribution")
        st.plotly_chart(fig3, use_container_width=True)

    with right:
        events = metrics.get("events", {})
        tool_df = pd.DataFrame(
            {
                "event": ["tool_invoked", "tool_blocked"],
                "count": [events.get("tool_invoked", 0), events.get("tool_blocked", 0)],
            }
        )
        fig4 = px.bar(tool_df, x="event", y="count", title="Tool Usage / Blocks")
        st.plotly_chart(fig4, use_container_width=True)

        policy_df = pd.DataFrame(
            {
                "metric": ["Policy Blocks", "Approvals Requested", "Approvals Granted"],
                "count": [
                    governance["prevented_critical_actions"],
                    governance["approvals_requested"],
                    governance["approvals_granted"],
                ],
            }
        )
        fig5 = px.bar(policy_df, x="metric", y="count", title="Policy / Approval Activity")
        st.plotly_chart(fig5, use_container_width=True)

        time_df = pd.DataFrame(
            {
                "mode": ["Estimated Manual", "AI-Assisted"],
                "minutes": [
                    productivity["estimated_manual_minutes"],
                    productivity["ai_assisted_minutes"],
                ],
            }
        )
        fig6 = px.bar(
            time_df,
            x="mode",
            y="minutes",
            title="Estimated Manual vs AI-Assisted Time (Simulated)",
        )
        st.plotly_chart(fig6, use_container_width=True)
else:
    st.warning("No telemetry yet. Run `python scripts/seed_metrics.py` or `make demo`.")

st.subheader("Recent Tasks")
if tasks:
    display = pd.DataFrame(tasks)[
        [
            "task_id",
            "task",
            "status",
            "risk_level",
            "approval_required",
            "tests_passed",
            "manual_minutes",
            "ai_minutes",
            "created_at",
        ]
    ]
    st.dataframe(display, use_container_width=True, hide_index=True)
else:
    st.write("No tasks recorded.")
