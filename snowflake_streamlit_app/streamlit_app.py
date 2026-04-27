import os
import io
import math
import zipfile
from pathlib import Path
from typing import Dict, Optional, Tuple

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


APP_DIR = Path(__file__).resolve().parent
DEFAULT_DATA_DIR = APP_DIR / "data" / "processed"
OUTPUT_FIG_DIR = APP_DIR / "outputs" / "figures"
OUTPUT_TABLE_DIR = APP_DIR / "outputs" / "tables"
RAW_DATA_DIR = APP_DIR / "data" / "raw"
DEFAULT_RAW_TELEMETRY_PATH = RAW_DATA_DIR / "generator_telemetry_with_labels.csv"
WSL_PROJECT_ROOT = Path("/mnt/c/Users/AnubhaAnubha/OneDrive - Pearce Services, LLC/onedrive_ubuntu/project/Predictive_Preventive_Maintenance_for_Generator_Reliability")
EXTERNAL_WSL_RAW_TELEMETRY_PATH = WSL_PROJECT_ROOT / "data" / "raw" / "generator_telemetry_with_labels.csv"


# Snowflake Streamlit does not support page_title/page_icon in st.set_page_config.
# Keep layout only and continue safely if the runtime ignores this call.
try:
    st.set_page_config(layout="wide", initial_sidebar_state="expanded")
except Exception:
    pass


# -----------------------------
# Utility helpers
# -----------------------------
def money(x):
    try:
        if pd.isna(x):
            return "$0"
        return f"${float(x):,.0f}"
    except Exception:
        return "$0"


def num(x, decimals=0):
    try:
        if pd.isna(x):
            return "0"
        return f"{float(x):,.{decimals}f}"
    except Exception:
        return "0"


def pct(x, decimals=1):
    try:
        if pd.isna(x):
            return "0%"
        return f"{float(x) * 100:.{decimals}f}%"
    except Exception:
        return "0%"


def read_csv_safely(path_or_buffer) -> pd.DataFrame:
    return pd.read_csv(path_or_buffer)


def parse_date_cols(df: pd.DataFrame, cols) -> pd.DataFrame:
    out = df.copy()
    for c in cols:
        if c in out.columns:
            out[c] = pd.to_datetime(out[c], errors="coerce")
    return out


@st.cache_data(show_spinner=False)
def load_default_tables() -> Dict[str, pd.DataFrame]:
    tables = {}
    files = {
        "asset_master": "asset_master.csv",
        "pm_events": "pm_events.csv",
        "failure_events": "failure_events.csv",
        "business_impact": "business_impact.csv",
        "pm_failure_linked": "pm_failure_linked.csv",
        "telemetry_weekly": "telemetry_weekly.csv",
    }
    for key, filename in files.items():
        path = DEFAULT_DATA_DIR / filename
        if path.exists():
            tables[key] = pd.read_csv(path)
        else:
            tables[key] = pd.DataFrame()

    tables["asset_master"] = parse_date_cols(tables["asset_master"], ["install_date"])
    tables["pm_events"] = parse_date_cols(tables["pm_events"], ["scheduled_date", "completed_date", "pm_date"])
    tables["failure_events"] = parse_date_cols(
        tables["failure_events"], ["failure_date", "ticket_open_date", "ticket_close_date"]
    )
    tables["business_impact"] = parse_date_cols(tables["business_impact"], ["event_date"])
    tables["pm_failure_linked"] = parse_date_cols(tables["pm_failure_linked"], ["pm_date", "next_failure_date"])
    tables["telemetry_weekly"] = parse_date_cols(tables["telemetry_weekly"], ["timestamp"])
    return tables


@st.cache_data(show_spinner=False)
def load_default_raw_telemetry() -> Tuple[pd.DataFrame, str]:
    """Load the raw telemetry file. Prefer the user's WSL project path when it exists; otherwise use the package copy."""
    if EXTERNAL_WSL_RAW_TELEMETRY_PATH.exists():
        df = pd.read_csv(EXTERNAL_WSL_RAW_TELEMETRY_PATH)
        return parse_date_cols(df, ["timestamp"]), str(EXTERNAL_WSL_RAW_TELEMETRY_PATH)
    if DEFAULT_RAW_TELEMETRY_PATH.exists():
        df = pd.read_csv(DEFAULT_RAW_TELEMETRY_PATH)
        return parse_date_cols(df, ["timestamp"]), str(DEFAULT_RAW_TELEMETRY_PATH)
    return pd.DataFrame(), "No raw telemetry file found"


def dataframe_profile(df: pd.DataFrame, source_path: str) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame({"Metric": ["Source path", "Rows", "Columns"], "Value": [source_path, "0", "0"]})
    values = {
        "Source path": source_path,
        "Rows": f"{len(df):,}",
        "Columns": f"{len(df.columns):,}",
        "Date range": "Not available",
        "Duplicate rows": f"{int(df.duplicated().sum()):,}",
        "Missing values": f"{int(df.isna().sum().sum()):,}",
    }
    if "timestamp" in df.columns:
        ts = pd.to_datetime(df["timestamp"], errors="coerce")
        if ts.notna().any():
            values["Date range"] = f"{ts.min().date()} to {ts.max().date()}"
    return pd.DataFrame({"Metric": list(values.keys()), "Value": list(values.values())})


def enrich_algorithm_output(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Create a transparent demo algorithm output from raw telemetry columns."""
    if raw_df.empty:
        return pd.DataFrame()
    out = raw_df.copy()
    if "timestamp" in out.columns:
        out["timestamp"] = pd.to_datetime(out["timestamp"], errors="coerce")
    for c in ["anomaly_score", "days_since_last_pm", "failure_within_30d", "failure_within_14d"]:
        if c in out.columns:
            out[c] = pd.to_numeric(out[c], errors="coerce")
    if "anomaly_score" not in out.columns:
        numeric_cols = out.select_dtypes(include=[np.number]).columns.tolist()
        if numeric_cols:
            z = out[numeric_cols].fillna(out[numeric_cols].median(numeric_only=True))
            out["anomaly_score"] = ((z - z.mean()) / z.std(ddof=0)).abs().mean(axis=1).rank(pct=True) * 100
        else:
            out["anomaly_score"] = 0
    conditions = [
        out["anomaly_score"] >= 80,
        out["anomaly_score"] >= 60,
        out["anomaly_score"] >= 40,
    ]
    choices = ["Critical", "High", "Watch"]
    out["algorithm_risk_band"] = np.select(conditions, choices, default="Low")
    pm_age = pd.to_numeric(out.get("days_since_last_pm", pd.Series(0, index=out.index)), errors="coerce").fillna(0)
    out["algorithm_failure_risk_score"] = np.clip((out["anomaly_score"].fillna(0) * 0.75) + np.minimum(pm_age, 180) / 180 * 25, 0, 100).round(2)
    out["algorithm_predicted_failure_within_30d"] = (out["algorithm_failure_risk_score"] >= 70).astype(int)
    out["recommended_action"] = np.select(
        [out["algorithm_risk_band"].eq("Critical"), out["algorithm_risk_band"].eq("High"), out["algorithm_risk_band"].eq("Watch")],
        ["Immediate inspection / corrective work order", "Schedule PM within 7 days", "Monitor and plan PM",],
        default="Normal monitoring",
    )
    sort_cols = [c for c in ["timestamp", "algorithm_failure_risk_score"] if c in out.columns]
    if sort_cols:
        out = out.sort_values(sort_cols, ascending=[False, False] if len(sort_cols) == 2 else False)
    return out


def summarize_algorithm_by_asset(algo_df: pd.DataFrame) -> pd.DataFrame:
    if algo_df.empty or "asset_id" not in algo_df.columns:
        return pd.DataFrame()
    df = algo_df.copy()
    if "timestamp" in df.columns:
        df = df.sort_values("timestamp")
    latest = df.groupby("asset_id", as_index=False).tail(1).copy()
    keep_cols = [c for c in ["asset_id", "timestamp", "model", "region", "criticality", "environment_type", "days_since_last_pm", "anomaly_score", "algorithm_failure_risk_score", "algorithm_risk_band", "algorithm_predicted_failure_within_30d", "recommended_action"] if c in latest.columns]
    return latest[keep_cols].sort_values("algorithm_failure_risk_score", ascending=False)


def identify_uploaded_zip(uploaded_zip) -> Dict[str, pd.DataFrame]:
    """Accepts a zip containing CSVs with expected names."""
    tables = {}
    if uploaded_zip is None:
        return tables

    expected = {
        "asset_master": "asset_master.csv",
        "pm_events": "pm_events.csv",
        "failure_events": "failure_events.csv",
        "business_impact": "business_impact.csv",
        "pm_failure_linked": "pm_failure_linked.csv",
        "telemetry_weekly": "telemetry_weekly.csv",
    }

    with zipfile.ZipFile(uploaded_zip) as z:
        names = z.namelist()
        for key, filename in expected.items():
            match = [n for n in names if n.endswith(filename)]
            if match:
                with z.open(match[0]) as f:
                    tables[key] = pd.read_csv(f)
    return tables


def build_pm_failure_linked(pm_df: pd.DataFrame, failure_df: pd.DataFrame) -> pd.DataFrame:
    required_pm = {"pm_event_id", "asset_id", "pm_date"}
    required_fail = {"failure_event_id", "asset_id", "failure_date"}

    if pm_df.empty or failure_df.empty:
        return pd.DataFrame()
    if not required_pm.issubset(pm_df.columns) or not required_fail.issubset(failure_df.columns):
        return pd.DataFrame()

    pm = parse_date_cols(pm_df, ["pm_date"]).copy()
    failures = parse_date_cols(failure_df, ["failure_date"]).copy()

    failure_groups = {}
    for asset_id, g in failures.dropna(subset=["failure_date"]).sort_values("failure_date").groupby("asset_id"):
        failure_groups[asset_id] = g.reset_index(drop=True)

    rows = []
    for _, row in pm.dropna(subset=["pm_date"]).iterrows():
        asset_id = row["asset_id"]
        pm_date = row["pm_date"]
        next_fail = None
        if asset_id in failure_groups:
            g = failure_groups[asset_id]
            pos = np.searchsorted(g["failure_date"].values.astype("datetime64[ns]"), np.datetime64(pm_date), side="right")
            if pos < len(g):
                next_fail = g.iloc[int(pos)]

        if next_fail is not None:
            days = (next_fail["failure_date"] - pm_date).days
            rows.append({
                "pm_event_id": row.get("pm_event_id"),
                "asset_id": asset_id,
                "pm_date": pm_date,
                "next_failure_event_id": next_fail.get("failure_event_id"),
                "next_failure_date": next_fail.get("failure_date"),
                "days_to_next_failure": days,
                "failure_found_flag": 1,
                "ontime_flag": row.get("ontime_flag", np.nan),
                "delay_days": row.get("delay_days", np.nan),
                "pm_total_cost": row.get("total_cost", np.nan),
                "failure_total_cost": next_fail.get("total_cost", np.nan),
                "failure_category": next_fail.get("failure_category", "Unknown"),
            })
        else:
            rows.append({
                "pm_event_id": row.get("pm_event_id"),
                "asset_id": asset_id,
                "pm_date": pm_date,
                "next_failure_event_id": None,
                "next_failure_date": pd.NaT,
                "days_to_next_failure": np.nan,
                "failure_found_flag": 0,
                "ontime_flag": row.get("ontime_flag", np.nan),
                "delay_days": row.get("delay_days", np.nan),
                "pm_total_cost": row.get("total_cost", np.nan),
                "failure_total_cost": np.nan,
                "failure_category": None,
            })

    return pd.DataFrame(rows)


def apply_asset_filters(tables: Dict[str, pd.DataFrame], regions, models, criticalities) -> Dict[str, pd.DataFrame]:
    assets = tables.get("asset_master", pd.DataFrame()).copy()
    if assets.empty:
        return tables

    mask = pd.Series(True, index=assets.index)
    if regions and "region" in assets.columns:
        mask &= assets["region"].isin(regions)
    if models and "model" in assets.columns:
        mask &= assets["model"].isin(models)
    if criticalities and "criticality" in assets.columns:
        mask &= assets["criticality"].isin(criticalities)

    keep_assets = set(assets.loc[mask, "asset_id"].astype(str))
    out = {}
    for key, df in tables.items():
        if isinstance(df, pd.DataFrame) and not df.empty and "asset_id" in df.columns:
            out[key] = df[df["asset_id"].astype(str).isin(keep_assets)].copy()
        else:
            out[key] = df.copy() if isinstance(df, pd.DataFrame) else df
    return out


def survival_curve(linked: pd.DataFrame) -> pd.DataFrame:
    if linked.empty or "days_to_next_failure" not in linked.columns:
        return pd.DataFrame(columns=["days", "failure_free_probability"])
    d = linked.loc[linked["days_to_next_failure"].notna(), "days_to_next_failure"].astype(float)
    if d.empty:
        return pd.DataFrame(columns=["days", "failure_free_probability"])
    days_grid = np.arange(0, max(30, int(d.max()) + 30), 30)
    n = len(d)
    vals = []
    for day in days_grid:
        vals.append({
            "days": int(day),
            "failure_free_probability": float((d > day).sum() / n)
        })
    return pd.DataFrame(vals)


def make_download_zip(tables: Dict[str, pd.DataFrame]) -> bytes:
    mem = io.BytesIO()
    with zipfile.ZipFile(mem, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for name, df in tables.items():
            if isinstance(df, pd.DataFrame) and not df.empty:
                z.writestr(f"{name}.csv", df.to_csv(index=False))
    mem.seek(0)
    return mem.read()


def metric_card(label, value, help_text=None):
    st.metric(label, value, help=help_text)


# -----------------------------
# Sidebar: data loading
# -----------------------------
st.sidebar.title("⚙️ Dashboard Controls")

st.sidebar.markdown(
    """
    **Data mode**
    - Default mode loads the included generator PM demo dataset.
    - Upload mode lets you override one or more CSVs.
    """
)

data_mode = st.sidebar.radio(
    "Choose data source",
    ["Use included default dataset", "Upload my own CSVs / ZIP"],
    index=0,
)

tables = load_default_tables()
raw_telemetry_df, raw_telemetry_source_path = load_default_raw_telemetry()

if data_mode == "Upload my own CSVs / ZIP":
    st.sidebar.info("Upload a ZIP with expected CSV names, or upload individual CSVs below. Missing files fall back to default data.")

    uploaded_zip = st.sidebar.file_uploader(
        "Optional: upload full data ZIP",
        type=["zip"],
        help="ZIP may contain asset_master.csv, pm_events.csv, failure_events.csv, telemetry_weekly.csv, business_impact.csv, pm_failure_linked.csv",
    )
    try:
        zip_tables = identify_uploaded_zip(uploaded_zip)
        for k, v in zip_tables.items():
            tables[k] = v
    except Exception as e:
        st.sidebar.error(f"Could not read ZIP: {e}")

    upload_specs = {
        "asset_master": "asset_master.csv",
        "pm_events": "pm_events.csv",
        "failure_events": "failure_events.csv",
        "business_impact": "business_impact.csv",
        "pm_failure_linked": "pm_failure_linked.csv",
        "telemetry_weekly": "telemetry_weekly.csv",
    }

    with st.sidebar.expander("Upload individual CSVs"):
        for key, label in upload_specs.items():
            f = st.file_uploader(label, type=["csv"], key=f"upload_{key}")
            if f is not None:
                try:
                    tables[key] = pd.read_csv(f)
                except Exception as e:
                    st.error(f"Could not read {label}: {e}")

    with st.sidebar.expander("Upload raw telemetry CSV"):
        raw_file = st.file_uploader(
            "generator_telemetry_with_labels.csv",
            type=["csv"],
            key="upload_raw_telemetry",
            help="Optional raw telemetry file before algorithm enrichment. If omitted, dashboard uses the WSL path when found, otherwise the included package file.",
        )
        if raw_file is not None:
            try:
                raw_telemetry_df = parse_date_cols(pd.read_csv(raw_file), ["timestamp"])
                raw_telemetry_source_path = "Uploaded file: generator_telemetry_with_labels.csv"
            except Exception as e:
                st.error(f"Could not read raw telemetry CSV: {e}")
# Parse dates after custom upload.
tables["asset_master"] = parse_date_cols(tables.get("asset_master", pd.DataFrame()), ["install_date"])
tables["pm_events"] = parse_date_cols(tables.get("pm_events", pd.DataFrame()), ["scheduled_date", "completed_date", "pm_date"])
tables["failure_events"] = parse_date_cols(tables.get("failure_events", pd.DataFrame()), ["failure_date", "ticket_open_date", "ticket_close_date"])
tables["business_impact"] = parse_date_cols(tables.get("business_impact", pd.DataFrame()), ["event_date"])
tables["pm_failure_linked"] = parse_date_cols(tables.get("pm_failure_linked", pd.DataFrame()), ["pm_date", "next_failure_date"])
tables["telemetry_weekly"] = parse_date_cols(tables.get("telemetry_weekly", pd.DataFrame()), ["timestamp"])
raw_telemetry_df = parse_date_cols(raw_telemetry_df, ["timestamp"])
algorithm_output_df = enrich_algorithm_output(raw_telemetry_df)
algorithm_asset_summary_df = summarize_algorithm_by_asset(algorithm_output_df)

# If the user uploaded PM/failure but not linked, rebuild it.
if tables.get("pm_failure_linked", pd.DataFrame()).empty and not tables.get("pm_events", pd.DataFrame()).empty and not tables.get("failure_events", pd.DataFrame()).empty:
    tables["pm_failure_linked"] = build_pm_failure_linked(tables["pm_events"], tables["failure_events"])

# Also allow forced rebuild.
if st.sidebar.button("Rebuild PM → Failure Links"):
    tables["pm_failure_linked"] = build_pm_failure_linked(tables["pm_events"], tables["failure_events"])
    st.sidebar.success("Rebuilt pm_failure_linked from PM and failure tables.")

assets = tables.get("asset_master", pd.DataFrame())
regions = []
models = []
criticalities = []
if not assets.empty:
    if "region" in assets.columns:
        all_regions = sorted([x for x in assets["region"].dropna().unique().tolist()])
        regions = st.sidebar.multiselect("Filter region", all_regions, default=all_regions)
    if "model" in assets.columns:
        all_models = sorted([x for x in assets["model"].dropna().unique().tolist()])
        models = st.sidebar.multiselect("Filter model", all_models, default=all_models)
    if "criticality" in assets.columns:
        all_criticality = sorted([x for x in assets["criticality"].dropna().unique().tolist()])
        criticalities = st.sidebar.multiselect("Filter criticality", all_criticality, default=all_criticality)

sample_limit = st.sidebar.slider("Telemetry chart sample size", 1_000, 50_000, 10_000, step=1_000)

filtered = apply_asset_filters(tables, regions, models, criticalities)

asset_df = filtered.get("asset_master", pd.DataFrame())
pm_df = filtered.get("pm_events", pd.DataFrame())
failure_df = filtered.get("failure_events", pd.DataFrame())
business_df = filtered.get("business_impact", pd.DataFrame())
linked_df = filtered.get("pm_failure_linked", pd.DataFrame())
telemetry_df = filtered.get("telemetry_weekly", pd.DataFrame())

# -----------------------------
# Header
# -----------------------------
st.title("⚙️ Generator Preventive Maintenance Reliability Dashboard")
st.caption("Upload your own maintenance data or use the included demo dataset to analyze PM effectiveness, failure risk, and business impact.")

with st.expander("Expected CSV inputs", expanded=False):
    st.markdown(
        """
        **Recommended CSVs**
        - `asset_master.csv`: one row per generator/asset
        - `pm_events.csv`: preventive maintenance events
        - `failure_events.csv`: unplanned repair/failure tickets
        - `pm_failure_linked.csv`: optional; dashboard can rebuild it
        - `telemetry_weekly.csv`: optional sensor/risk history
        - `business_impact.csv`: optional downtime, repair cost, customer impact

        **Minimum required for Jeff-style analysis**
        - `pm_events.csv` with `pm_event_id`, `asset_id`, `pm_date`
        - `failure_events.csv` with `failure_event_id`, `asset_id`, `failure_date`
        """
    )

# -----------------------------
# Tabs
# -----------------------------
tabs = st.tabs([
    "Problem & Solution",
    "Dataset & Raw → Algorithm",
    "Executive KPIs",
    "PM Effectiveness",
    "Failures & Cost",
    "Telemetry Risk",
    "Saved Outputs",
    "Data Explorer & Export",
])


# -----------------------------
# Problem & Solution tab
# -----------------------------
with tabs[0]:
    st.header("Problem Statement")
    st.markdown(
        """
        Telecom and field-service teams need to know whether **preventive maintenance is actually preventing generator failures**.

        The key business question is:

        > After a PM is completed, how long does a generator typically run before the next failure or repair ticket?

        Without this, teams cannot confidently answer:
        - Which PMs are effective?
        - Which assets are becoming risky?
        - How much downtime and cost can be avoided?
        - Which regions, models, or environments need more attention?
        """
    )

    st.header("Solution Provided")
    st.markdown(
        """
        This dashboard converts maintenance records into a reliability workflow:

        1. **Load data**  
           Use the included generator demo dataset or upload your own CSVs.

        2. **Link PM to next failure**  
           For every PM event, the dashboard finds the first later failure ticket for the same asset.

        3. **Measure PM effectiveness**  
           It calculates `days_to_next_failure`, failure-free rate, and on-time vs delayed PM comparisons.

        4. **Analyze failure cost and downtime**  
           It summarizes repair cost, truck-roll cost, downtime, SLA impact, and customer impact.

        5. **Add risk layer**  
           Telemetry and anomaly signals show which assets are most likely to fail soon.

        6. **Export outputs**  
           KPI tables and processed datasets can be downloaded for Power BI, Excel, Streamlit sharing, or a client deck.
        """
    )

    st.subheader("Architecture")
    st.code(
        """
PM Events + Failure Tickets + Asset Master
          │
          ▼
PM → Next Failure Linker
          │
          ├── PM effectiveness KPIs
          ├── Failure-free survival curve
          ├── On-time vs delayed PM comparison
          ├── Failure cost and downtime view
          └── Telemetry risk overlay
        """,
        language="text",
    )

    st.subheader("Dataset currently loaded")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Assets", f"{len(asset_df):,}")
    c2.metric("PM events", f"{len(pm_df):,}")
    c3.metric("Failure tickets", f"{len(failure_df):,}")
    c4.metric("Telemetry rows", f"{len(telemetry_df):,}")
    c5.metric("Linked PM rows", f"{len(linked_df):,}")


# -----------------------------
# -----------------------------
# Dataset and Raw → Algorithm tab
# -----------------------------
with tabs[1]:
    st.header("Dataset Used: Raw → Algorithm Output")
    st.markdown(
        """
        This page explains exactly what data is being used, where it is expected in WSL, what the raw file looks like before the algorithm, and what the algorithm produces after enrichment.

        **Primary raw dataset expected by the project:**
        """
    )
    st.code(str(EXTERNAL_WSL_RAW_TELEMETRY_PATH), language="bash")
    st.markdown("**Package fallback raw dataset:**")
    st.code(str(DEFAULT_RAW_TELEMETRY_PATH), language="bash")

    st.info(
        f"Currently loaded raw telemetry source: {raw_telemetry_source_path}\n\n"
        "The dashboard first checks the WSL project path you provided. If that file is not present, it uses the packaged demo raw file."
    )

    st.subheader("1) Raw dataset profile before algorithm")
    st.dataframe(dataframe_profile(raw_telemetry_df, raw_telemetry_source_path), use_container_width=True)

    if raw_telemetry_df.empty:
        st.warning("Raw telemetry dataset is not available. Place generator_telemetry_with_labels.csv at the WSL path above or upload it from the sidebar.")
    else:
        c1, c2 = st.columns([2, 1])
        with c1:
            st.markdown("**Raw telemetry preview**")
            st.dataframe(raw_telemetry_df.head(1000), use_container_width=True)
        with c2:
            missing = raw_telemetry_df.isna().sum().sort_values(ascending=False).head(12).reset_index()
            missing.columns = ["column", "missing_count"]
            fig = px.bar(missing, x="missing_count", y="column", orientation="h", title="Raw missing values by column")
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("**Raw signal visualizations before algorithm**")
        c3, c4 = st.columns(2)
        with c3:
            if "anomaly_score" in raw_telemetry_df.columns:
                fig = px.histogram(raw_telemetry_df, x="anomaly_score", nbins=50, title="Raw anomaly score distribution")
                st.plotly_chart(fig, use_container_width=True)
            elif "runtime_hours_week" in raw_telemetry_df.columns:
                fig = px.histogram(raw_telemetry_df, x="runtime_hours_week", nbins=50, title="Raw weekly runtime distribution")
                st.plotly_chart(fig, use_container_width=True)
        with c4:
            signal_cols = [c for c in ["oil_temp_c", "coolant_temp_c", "battery_voltage", "vibration_mm_s", "fuel_rate_lph", "runtime_hours_week"] if c in raw_telemetry_df.columns]
            if signal_cols and "timestamp" in raw_telemetry_df.columns:
                sample_asset = raw_telemetry_df["asset_id"].iloc[0] if "asset_id" in raw_telemetry_df.columns else None
                signal = signal_cols[0]
                plot_df = raw_telemetry_df[raw_telemetry_df["asset_id"].eq(sample_asset)].copy() if sample_asset and "asset_id" in raw_telemetry_df.columns else raw_telemetry_df.head(200)
                fig = px.line(plot_df.sort_values("timestamp"), x="timestamp", y=signal, title=f"Raw signal trend example: {signal}")
                st.plotly_chart(fig, use_container_width=True)

        st.subheader("2) Algorithm applied")
        st.markdown(
            """
            The dashboard creates a transparent demo algorithm layer from the raw telemetry:

            - Uses `anomaly_score` as the main health signal.
            - Adds PM-age pressure using `days_since_last_pm`.
            - Produces `algorithm_failure_risk_score` on a 0–100 scale.
            - Converts risk score into `Low`, `Watch`, `High`, or `Critical` bands.
            - Adds `algorithm_predicted_failure_within_30d` and a recommended maintenance action.

            This is intentionally explainable for a business demo. When real client data is available, this layer can be replaced by a trained classifier, survival model, or remaining-useful-life model.
            """
        )

        st.code(
            """
algorithm_failure_risk_score = 0.75 * anomaly_score + 0.25 * normalized_days_since_last_pm
risk bands:
  Low      < 40
  Watch    40–59
  High     60–79
  Critical >= 80
prediction:
  predicted_failure_within_30d = 1 when risk_score >= 70
            """.strip(),
            language="text",
        )

        st.subheader("3) After algorithm: enriched output")
        if algorithm_output_df.empty:
            st.warning("Algorithm output is empty because no raw telemetry was loaded.")
        else:
            c5, c6, c7, c8 = st.columns(4)
            c5.metric("Raw rows processed", f"{len(raw_telemetry_df):,}")
            c6.metric("Algorithm output rows", f"{len(algorithm_output_df):,}")
            c7.metric("Assets scored", f"{algorithm_output_df['asset_id'].nunique():,}" if "asset_id" in algorithm_output_df.columns else "0")
            c8.metric("Predicted 30-day failures", f"{int(algorithm_output_df.get('algorithm_predicted_failure_within_30d', pd.Series(dtype=int)).sum()):,}")

            c9, c10 = st.columns(2)
            with c9:
                risk_counts = algorithm_output_df["algorithm_risk_band"].value_counts().reindex(["Low", "Watch", "High", "Critical"]).dropna().reset_index()
                risk_counts.columns = ["risk_band", "row_count"]
                fig = px.bar(risk_counts, x="risk_band", y="row_count", title="After algorithm: risk-band distribution")
                st.plotly_chart(fig, use_container_width=True)
            with c10:
                if {"region", "algorithm_predicted_failure_within_30d"}.issubset(algorithm_output_df.columns):
                    region_risk = algorithm_output_df.groupby("region", as_index=False)["algorithm_predicted_failure_within_30d"].sum()
                    fig = px.bar(region_risk, x="region", y="algorithm_predicted_failure_within_30d", title="Predicted 30-day failures by region")
                    st.plotly_chart(fig, use_container_width=True)

            st.markdown("**Algorithm output preview**")
            output_cols = [c for c in ["asset_id", "timestamp", "model", "region", "criticality", "days_since_last_pm", "anomaly_score", "algorithm_failure_risk_score", "algorithm_risk_band", "algorithm_predicted_failure_within_30d", "recommended_action"] if c in algorithm_output_df.columns]
            st.dataframe(algorithm_output_df[output_cols].head(2000), use_container_width=True)

            st.markdown("**Latest asset-level output after algorithm**")
            st.dataframe(algorithm_asset_summary_df.head(500), use_container_width=True)

            st.download_button(
                "Download algorithm_output.csv",
                data=algorithm_output_df.to_csv(index=False),
                file_name="algorithm_output.csv",
                mime="text/csv",
            )
            st.download_button(
                "Download latest_asset_risk_summary.csv",
                data=algorithm_asset_summary_df.to_csv(index=False),
                file_name="latest_asset_risk_summary.csv",
                mime="text/csv",
            )

    st.subheader("4) WSL commands to run dashboard")
    st.code(
        """
cd "/mnt/c/Users/AnubhaAnubha/OneDrive - Pearce Services, LLC/onedrive_ubuntu/project/Predictive_Preventive_Maintenance_for_Generator_Reliability"
pip install -r requirements.txt
streamlit run app.py
        """.strip(),
        language="bash",
    )

# Executive KPIs tab
# -----------------------------
with tabs[2]:
    st.header("Executive KPIs")

    valid_days = pd.Series(dtype=float)
    if not linked_df.empty and "days_to_next_failure" in linked_df.columns:
        valid_days = pd.to_numeric(linked_df["days_to_next_failure"], errors="coerce").dropna()

    avg_days = valid_days.mean() if not valid_days.empty else np.nan
    median_days = valid_days.median() if not valid_days.empty else np.nan
    fail_30 = (valid_days <= 30).mean() if not valid_days.empty else np.nan
    fail_90 = (valid_days <= 90).mean() if not valid_days.empty else np.nan

    total_downtime = pd.to_numeric(failure_df.get("downtime_hours", pd.Series(dtype=float)), errors="coerce").sum()
    total_failure_cost = pd.to_numeric(failure_df.get("total_cost", pd.Series(dtype=float)), errors="coerce").sum()

    total_revenue_loss = 0
    total_customers = 0
    if not business_df.empty:
        total_revenue_loss = pd.to_numeric(business_df.get("estimated_revenue_loss", pd.Series(dtype=float)), errors="coerce").sum()
        total_customers = pd.to_numeric(business_df.get("estimated_customers_impacted", pd.Series(dtype=float)), errors="coerce").sum()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Avg days PM → failure", num(avg_days, 1))
    c2.metric("Median days PM → failure", num(median_days, 1))
    c3.metric("Failure within 30 days", pct(fail_30))
    c4.metric("Failure within 90 days", pct(fail_90))

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Total downtime hours", num(total_downtime, 1))
    c6.metric("Failure repair cost", money(total_failure_cost))
    c7.metric("Estimated revenue loss", money(total_revenue_loss))
    c8.metric("Customer impact count", num(total_customers, 0))

    st.divider()

    st.subheader("Executive interpretation")
    st.markdown(
        f"""
        - The loaded data contains **{len(asset_df):,} assets**, **{len(pm_df):,} PM events**, and **{len(failure_df):,} failure/repair tickets**.
        - The average observed time from PM to the next failure is **{num(avg_days, 1)} days**.
        - **{pct(fail_30)}** of linked PM events are followed by a failure within 30 days.
        - The failure records represent approximately **{num(total_downtime, 1)} downtime hours** and **{money(total_failure_cost)}** in repair cost.
        """
    )

    if not linked_df.empty and "failure_found_flag" in linked_df.columns:
        status_counts = linked_df["failure_found_flag"].value_counts().rename(index={0: "No later failure observed", 1: "Later failure observed"})
        fig = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title="Linked PM events with later failure observed",
            hole=0.35,
        )
        st.plotly_chart(fig, use_container_width=True)


# -----------------------------
# PM Effectiveness tab
# -----------------------------
with tabs[3]:
    st.header("Preventive Maintenance Effectiveness")

    if linked_df.empty or "days_to_next_failure" not in linked_df.columns:
        st.warning("No PM-to-failure linked data found. Upload PM and failure CSVs, then click 'Rebuild PM → Failure Links'.")
    else:
        linked_plot = linked_df.copy()
        linked_plot["days_to_next_failure"] = pd.to_numeric(linked_plot["days_to_next_failure"], errors="coerce")

        c1, c2 = st.columns(2)

        with c1:
            fig = px.histogram(
                linked_plot.dropna(subset=["days_to_next_failure"]),
                x="days_to_next_failure",
                nbins=50,
                title="Distribution: Days from PM to next failure",
                labels={"days_to_next_failure": "Days to next failure"},
            )
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            surv = survival_curve(linked_plot)
            if not surv.empty:
                fig = px.line(
                    surv,
                    x="days",
                    y="failure_free_probability",
                    markers=True,
                    title="Failure-free probability after PM",
                    labels={"days": "Days after PM", "failure_free_probability": "Failure-free probability"},
                )
                fig.update_yaxes(tickformat=".0%")
                st.plotly_chart(fig, use_container_width=True)

        c3, c4 = st.columns(2)
        with c3:
            if "ontime_flag" in linked_plot.columns:
                temp = linked_plot.dropna(subset=["ontime_flag", "days_to_next_failure"]).copy()
                if not temp.empty:
                    temp["PM status"] = temp["ontime_flag"].map({1: "On-time PM", 0: "Delayed PM"}).fillna("Unknown")
                    fig = px.box(
                        temp,
                        x="PM status",
                        y="days_to_next_failure",
                        points="outliers",
                        title="On-time vs delayed PM: Days to next failure",
                    )
                    st.plotly_chart(fig, use_container_width=True)

        with c4:
            if "delay_days" in linked_plot.columns:
                temp = linked_plot.dropna(subset=["delay_days", "days_to_next_failure"]).copy()
                if not temp.empty:
                    fig = px.scatter(
                        temp.sample(min(len(temp), 5000), random_state=42),
                        x="delay_days",
                        y="days_to_next_failure",
                        trendline="ols",
                        title="PM delay vs days to next failure",
                        labels={"delay_days": "PM delay days", "days_to_next_failure": "Days to next failure"},
                    )
                    st.plotly_chart(fig, use_container_width=True)

        st.subheader("PM effectiveness data")
        st.dataframe(linked_plot.head(1000), use_container_width=True)


# -----------------------------
# Failures & Cost tab
# -----------------------------
with tabs[4]:
    st.header("Failure Patterns, Cost, and Downtime")

    if failure_df.empty:
        st.warning("No failure_events.csv data found.")
    else:
        c1, c2 = st.columns(2)

        with c1:
            if "failure_category" in failure_df.columns:
                cat = failure_df["failure_category"].fillna("Unknown").value_counts().reset_index()
                cat.columns = ["failure_category", "count"]
                fig = px.bar(cat, x="failure_category", y="count", title="Failures by category")
                st.plotly_chart(fig, use_container_width=True)

        with c2:
            if "severity" in failure_df.columns:
                sev = failure_df["severity"].fillna("Unknown").value_counts().reset_index()
                sev.columns = ["severity", "count"]
                fig = px.bar(sev, x="severity", y="count", title="Failures by severity")
                st.plotly_chart(fig, use_container_width=True)

        c3, c4 = st.columns(2)

        with c3:
            if {"region", "total_cost"}.issubset(failure_df.columns):
                temp = failure_df.copy()
                temp["total_cost"] = pd.to_numeric(temp["total_cost"], errors="coerce")
                reg = temp.groupby("region", as_index=False)["total_cost"].sum()
                fig = px.bar(reg, x="region", y="total_cost", title="Repair cost by region")
                st.plotly_chart(fig, use_container_width=True)

        with c4:
            if {"model", "downtime_hours"}.issubset(failure_df.columns):
                temp = failure_df.copy()
                temp["downtime_hours"] = pd.to_numeric(temp["downtime_hours"], errors="coerce")
                mod = temp.groupby("model", as_index=False)["downtime_hours"].sum().sort_values("downtime_hours", ascending=False)
                fig = px.bar(mod, x="model", y="downtime_hours", title="Downtime hours by model")
                st.plotly_chart(fig, use_container_width=True)

        if not business_df.empty:
            st.subheader("Business impact")
            b1, b2, b3 = st.columns(3)
            b1.metric("Truck-roll cost", money(pd.to_numeric(business_df.get("truck_roll_cost", pd.Series(dtype=float)), errors="coerce").sum()))
            b2.metric("Revenue loss", money(pd.to_numeric(business_df.get("estimated_revenue_loss", pd.Series(dtype=float)), errors="coerce").sum()))
            b3.metric("SLA breach events", num(pd.to_numeric(business_df.get("sla_breach_flag", pd.Series(dtype=float)), errors="coerce").sum(), 0))

            if {"event_date", "estimated_revenue_loss"}.issubset(business_df.columns):
                temp = business_df.copy()
                temp["event_month"] = pd.to_datetime(temp["event_date"], errors="coerce").dt.to_period("M").astype(str)
                temp["estimated_revenue_loss"] = pd.to_numeric(temp["estimated_revenue_loss"], errors="coerce")
                month = temp.groupby("event_month", as_index=False)["estimated_revenue_loss"].sum()
                fig = px.line(month, x="event_month", y="estimated_revenue_loss", markers=True, title="Estimated revenue loss over time")
                st.plotly_chart(fig, use_container_width=True)


# -----------------------------
# Telemetry Risk tab
# -----------------------------
with tabs[5]:
    st.header("Telemetry and Failure Risk")

    if telemetry_df.empty:
        st.warning("No telemetry_weekly.csv data found.")
    else:
        tele = telemetry_df.copy()
        for col in ["anomaly_score", "days_since_last_pm", "days_to_next_failure", "failure_within_30d"]:
            if col in tele.columns:
                tele[col] = pd.to_numeric(tele[col], errors="coerce")

        high_risk = pd.DataFrame()
        if "anomaly_score" in tele.columns:
            latest = tele.sort_values("timestamp").groupby("asset_id", as_index=False).tail(1)
            high_risk = latest.sort_values("anomaly_score", ascending=False).head(25)

            c1, c2, c3 = st.columns(3)
            c1.metric("Latest high-risk assets shown", f"{len(high_risk):,}")
            c2.metric("Avg anomaly score", num(tele["anomaly_score"].mean(), 1))
            if "failure_within_30d" in tele.columns:
                c3.metric("Rows labeled failure within 30d", f"{int(tele['failure_within_30d'].sum()):,}")

        c1, c2 = st.columns(2)

        with c1:
            if {"days_since_last_pm", "anomaly_score"}.issubset(tele.columns):
                sample = tele.dropna(subset=["days_since_last_pm", "anomaly_score"])
                sample = sample.sample(min(len(sample), sample_limit), random_state=42) if len(sample) > sample_limit else sample
                color_col = "failure_within_30d" if "failure_within_30d" in sample.columns else None
                fig = px.scatter(
                    sample,
                    x="days_since_last_pm",
                    y="anomaly_score",
                    color=color_col,
                    hover_data=["asset_id"] if "asset_id" in sample.columns else None,
                    title="Anomaly score vs days since last PM",
                )
                st.plotly_chart(fig, use_container_width=True)

        with c2:
            if {"days_since_last_pm", "anomaly_score"}.issubset(tele.columns):
                temp = tele.dropna(subset=["days_since_last_pm", "anomaly_score"]).copy()
                temp["pm_age_bucket"] = pd.cut(temp["days_since_last_pm"], bins=[0, 30, 60, 90, 120, 180, 365, 10000])
                bucket = temp.groupby("pm_age_bucket", observed=True, as_index=False)["anomaly_score"].mean()
                bucket["pm_age_bucket"] = bucket["pm_age_bucket"].astype(str)
                fig = px.bar(bucket, x="pm_age_bucket", y="anomaly_score", title="Average anomaly score by PM age bucket")
                st.plotly_chart(fig, use_container_width=True)

        st.subheader("Top risky assets by latest anomaly score")
        if not high_risk.empty:
            st.dataframe(high_risk, use_container_width=True)


# -----------------------------
# Saved Outputs tab
# -----------------------------
with tabs[6]:
    st.header("Saved Outputs Included in Package")
    st.markdown("These are pre-generated figures and tables from the notebook workflow.")

    fig_files = sorted([p for p in OUTPUT_FIG_DIR.glob("*.png")]) if OUTPUT_FIG_DIR.exists() else []
    if fig_files:
        for p in fig_files:
            st.subheader(p.stem.replace("_", " ").title())
            st.image(str(p), use_container_width=True)
    else:
        st.info("No saved PNG figures found in outputs/figures.")

    st.divider()
    table_files = sorted([p for p in OUTPUT_TABLE_DIR.glob("*.csv")]) if OUTPUT_TABLE_DIR.exists() else []
    if table_files:
        st.subheader("Saved output tables")
        for p in table_files:
            with st.expander(p.name):
                try:
                    df = pd.read_csv(p)
                    st.dataframe(df.head(500), use_container_width=True)
                    st.download_button(
                        f"Download {p.name}",
                        data=df.to_csv(index=False),
                        file_name=p.name,
                        mime="text/csv",
                    )
                except Exception as e:
                    st.error(f"Could not read {p.name}: {e}")
    else:
        st.info("No saved CSV tables found in outputs/tables.")


# -----------------------------
# Data Explorer & Export tab
# -----------------------------
with tabs[7]:
    st.header("Data Explorer and Export")

    table_options = {
        "asset_master": asset_df,
        "pm_events": pm_df,
        "failure_events": failure_df,
        "business_impact": business_df,
        "pm_failure_linked": linked_df,
        "telemetry_weekly": telemetry_df,
        "raw_telemetry_before_algorithm": raw_telemetry_df,
        "algorithm_output_after_algorithm": algorithm_output_df,
        "latest_asset_risk_summary": algorithm_asset_summary_df,
    }

    selected = st.selectbox("Choose table", list(table_options.keys()))
    df = table_options[selected]

    if df.empty:
        st.warning(f"{selected} is empty.")
    else:
        st.write(f"Rows: **{len(df):,}** | Columns: **{len(df.columns):,}**")
        st.dataframe(df.head(5000), use_container_width=True)
        st.download_button(
            f"Download filtered {selected}.csv",
            data=df.to_csv(index=False),
            file_name=f"{selected}_filtered.csv",
            mime="text/csv",
        )

    st.divider()
    st.subheader("Download all currently filtered dashboard tables")
    zip_bytes = make_download_zip(table_options)
    st.download_button(
        "Download filtered dashboard data ZIP",
        data=zip_bytes,
        file_name="filtered_generator_pm_dashboard_data.zip",
        mime="application/zip",
    )

    st.subheader("Data quality checklist")
    checks = []
    checks.append(("PM table has asset_id", "asset_id" in pm_df.columns if not pm_df.empty else False))
    checks.append(("PM table has pm_date", "pm_date" in pm_df.columns if not pm_df.empty else False))
    checks.append(("Failure table has asset_id", "asset_id" in failure_df.columns if not failure_df.empty else False))
    checks.append(("Failure table has failure_date", "failure_date" in failure_df.columns if not failure_df.empty else False))
    checks.append(("Linked table available", not linked_df.empty))
    checks.append(("Telemetry table available", not telemetry_df.empty))
    checks.append(("Business impact table available", not business_df.empty))

    check_df = pd.DataFrame(checks, columns=["Check", "Passed"])
    st.dataframe(check_df, use_container_width=True)
