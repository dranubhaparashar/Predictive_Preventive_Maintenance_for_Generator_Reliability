# Predictive Preventive Maintenance for Generator Reliability

A full-stack analytics and machine-learning dashboard for measuring **preventive maintenance effectiveness**, predicting **near-term generator failure risk**, and recommending **priority maintenance actions**.

This project demonstrates how generator maintenance records, failure tickets, telemetry signals, and business-impact data can be converted into an end-to-end reliability workflow.

---

## Project Objective

Preventive maintenance is only useful if it can be measured.

This project answers the key business question:

> After a preventive maintenance event is completed, how long does a generator continue running before the next failure or repair ticket?

The dashboard helps teams understand:

- Whether preventive maintenance is improving generator reliability.
- Which assets fail soon after PM.
- Whether delayed PM is associated with higher risk.
- Which models, regions, or environments need more attention.
- Which generators are likely to fail within the next 14 or 30 days.
- Which assets should be prioritized for inspection or maintenance.
- How downtime, repair cost, truck-roll cost, and customer impact can be analyzed.

---

## Live Links

- **Live Hugging Face Dashboard:**  
  https://huggingface.co/spaces/AnubhaParashar/Predictive_Preventive_Maintenance_for_Generator_Reliability

- **Demo Video:**  
  https://www.youtube.com/watch?v=QQSSFWxY_ro

- **Architecture Wiki:**  
  https://github.com/dranubhaparashar/Predictive_Preventive_Maintenance_for_Generator_Reliability/wiki/Architecture-%E2%80%90-Generator-PM-Reliability-Dashboard

- **Function Reference Wiki:**  
  https://github.com/dranubhaparashar/Predictive_Preventive_Maintenance_for_Generator_Reliability/wiki/Function-Reference-%E2%80%90-Generator-PM-Reliability-Dashboard

- **Technical Wiki:**  
  https://github.com/dranubhaparashar/Predictive_Preventive_Maintenance_for_Generator_Reliability/wiki/Predictive-Preventive-Maintenance-for-Generator-Reliability

---

## Executive Summary

This dashboard is a proof-of-concept for generator reliability analytics.

It shows how maintenance teams can move from simple PM tracking to a more advanced workflow:

```text
PM completed
    -> next failure linked
    -> days to next failure calculated
    -> downtime and cost analyzed
    -> telemetry risk scored
    -> ML model predicts near-term failure
    -> recommended PM action generated
```

The current version uses a **synthetic generator maintenance dataset** created for demonstration. It is not real production or customer data. The workflow is designed so real generator PM records, failure tickets, telemetry, and business-impact data can replace the demo dataset later.

---

## What PM Means

**PM** stands for **Preventive Maintenance**.

In this project, PM means planned maintenance performed before a generator fails. Examples include:

- routine inspection
- oil and filter change
- battery check
- coolant check
- fuel system check
- load testing
- alarm review
- vibration and temperature checks
- electrical and mechanical inspection

The dashboard measures how effective these PM events are by checking what happens after each PM is completed.

---

## Core Problem Statement

Field-service and telecom teams need a data-backed way to prove whether preventive maintenance actually reduces generator failures.

The dashboard is designed to answer:

```text
After PM is completed, how many days does the generator remain failure-free?
```

Without this analysis, teams cannot confidently answer:

- Which PMs are effective?
- Which generators are becoming risky?
- Are delayed PMs associated with earlier failures?
- What is the cost of failures?
- Which assets should be inspected first?
- Can telemetry signals predict failures before they happen?

---

## Solution Overview

The solution has three major phases.

### Phase 1: Reliability Analytics

This phase is deterministic and explainable.

It links every PM event to the next failure ticket for the same generator.

```text
PM event -> same asset_id -> first later failure -> days_to_next_failure
```

Main output:

```text
days_to_next_failure
```

This measures how long the generator survived after preventive maintenance.

### Phase 2: Predictive Machine Learning

This phase trains supervised ML models using telemetry and failure labels.

Models used:

- Logistic Regression baseline
- Random Forest advanced model

Prediction targets:

- `failure_within_14d`
- `failure_within_30d`

The ML section produces:

- model comparison metrics
- confusion matrix
- feature importance
- asset-level predicted failure risk
- ML risk bands

### Phase 3: Prescriptive PM Strategy

This phase converts analytics and ML predictions into maintenance actions.

It combines:

- predicted failure risk
- historical PM-to-failure behavior
- days since last PM
- anomaly score
- alarm count
- downtime and failure cost exposure

Recommended actions include:

- immediate inspection
- PM within 3 days
- PM within 7 days
- watch list / monitor closely
- normal monitoring

---

## Key Features

- Interactive Streamlit dashboard
- Upload your own CSV files or ZIP
- Use included default demo dataset
- PM-to-next-failure linking
- PM effectiveness analytics
- On-time vs delayed PM comparison
- Executive KPI dashboard
- Failure cost and downtime analysis
- Business-impact analysis
- Telemetry risk visualization
- Predictive ML tab
- Logistic Regression baseline model
- Random Forest advanced model
- Feature importance visualization
- Asset-level ML risk scoring
- Prescriptive PM action planning
- Downloadable filtered datasets
- Hugging Face deployment support
- Snowflake Streamlit deployment support
- Docker deployment support

---

## Dataset Used

The current dashboard uses an included **synthetic generator maintenance dataset** created for this proof-of-concept.

It is not real customer data, production data, or Verizon/Pearce operational data.

The dataset is structured like the real production data that would be needed:

- generator asset master
- preventive maintenance events
- failure and repair tickets
- telemetry signals
- PM-to-failure linked output
- business impact fields

Public predictive-maintenance datasets were used only as methodology references, not as direct data sources.

---

## Input Files

The dashboard expects these files.

### `asset_master.csv`

One row per generator asset.

Typical fields:

- `asset_id`
- `asset_name`
- `asset_type`
- `manufacturer`
- `model`
- `install_date`
- `location`
- `region`
- `criticality`
- `environment_type`
- `service_interval_days`

### `pm_events.csv`

Preventive maintenance event records.

Typical fields:

- `pm_event_id`
- `asset_id`
- `scheduled_date`
- `completed_date`
- `pm_date`
- `pm_type`
- `status`
- `delay_days`
- `ontime_flag`
- `priority`
- `total_cost`

### `failure_events.csv`

Failure and repair ticket records.

Typical fields:

- `failure_event_id`
- `asset_id`
- `failure_date`
- `ticket_open_date`
- `ticket_close_date`
- `failure_category`
- `severity`
- `priority`
- `downtime_hours`
- `total_cost`
- `root_cause`

### `pm_failure_linked.csv`

Derived reliability output.

Typical fields:

- `pm_event_id`
- `asset_id`
- `pm_date`
- `next_failure_event_id`
- `next_failure_date`
- `days_to_next_failure`
- `failure_found_flag`
- `ontime_flag`
- `delay_days`
- `pm_total_cost`
- `failure_total_cost`

### `telemetry_weekly.csv`

Weekly telemetry and risk history.

Typical fields:

- `asset_id`
- `timestamp`
- `days_since_last_pm`
- `runtime_hours_week`
- `avg_load_pct`
- `oil_temp_c`
- `coolant_temp_c`
- `battery_voltage`
- `vibration_mm_s`
- `fuel_rate_lph`
- `alarm_count`
- `anomaly_score`
- `failure_within_14d`
- `failure_within_30d`

### `generator_telemetry_with_labels.csv`

Raw telemetry with ML labels.

This file is used for predictive modeling.

Important labels:

- `failure_within_14d`
- `failure_within_30d`

### `business_impact.csv`

Failure impact and cost data.

Typical fields:

- `asset_id`
- `failure_event_id`
- `event_date`
- `downtime_hours`
- `truck_roll_cost`
- `repair_cost`
- `estimated_customers_impacted`
- `estimated_revenue_loss`
- `sla_breach_flag`

---

## Folder Structure

```text
Predictive_Preventive_Maintenance_for_Generator_Reliability/
│
├── app.py
├── streamlit_app.py
├── requirements.txt
├── environment.yml
├── Dockerfile
├── README.md
│
├── data/
│   ├── raw/
│   │   └── generator_telemetry_with_labels.csv
│   │
│   └── processed/
│       ├── asset_master.csv
│       ├── pm_events.csv
│       ├── failure_events.csv
│       ├── business_impact.csv
│       ├── pm_failure_linked.csv
│       └── telemetry_weekly.csv
│
├── outputs/
│   ├── figures/
│   └── tables/
│
├── docs/
├── notebooks/
├── scripts/
├── sql/
└── snowflake_streamlit_app/
```

---

## Main Algorithm

### PM-to-Next-Failure Linking

The core reliability algorithm works as follows:

```text
For each PM event:
    1. Take asset_id and pm_date.
    2. Search all failure events for the same asset_id.
    3. Keep only failures that happened after pm_date.
    4. Select the earliest later failure.
    5. Calculate days_to_next_failure.
    6. Save the linked PM-to-failure row.
```

Main metric:

```text
days_to_next_failure = next_failure_date - pm_date
```

This tells us how long the generator stayed failure-free after PM.

---

## Machine Learning Approach

The dashboard trains supervised classification models.

### ML Inputs

Features include:

- `days_since_last_pm`
- `runtime_hours_week`
- `avg_load_pct`
- `oil_temp_c`
- `coolant_temp_c`
- `battery_voltage`
- `vibration_mm_s`
- `fuel_rate_lph`
- `alarm_count`
- `anomaly_score`
- `model`
- `region`
- `criticality`
- `environment_type`

### ML Targets

The user can select:

- `failure_within_14d`
- `failure_within_30d`

### Models Used

#### Logistic Regression

Used as the baseline model.

Why it is useful:

- easy to explain
- good benchmark
- interpretable relationship between features and risk

#### Random Forest Classifier

Used as the advanced model.

Why it is useful:

- captures nonlinear relationships
- handles feature interactions
- works well for risk-ranking operational assets

### ML Outputs

The ML tab shows:

- Accuracy
- Precision
- Recall
- F1 score
- ROC AUC
- Confusion matrix
- Top predictive drivers
- Asset-level failure probability
- Risk bands
- Recommended maintenance action

---

## Dashboard Tabs

### Problem & Solution

Explains the business problem, solution, and overall workflow.

### Dataset & Raw → Algorithm

Shows raw telemetry profile, raw preview, missing values, algorithm explanation, and enriched output.

### Executive KPIs

Shows high-level metrics such as:

- average days from PM to failure
- median days from PM to failure
- failure within 30 days
- failure within 90 days
- total downtime hours
- repair cost
- estimated revenue loss
- customer impact

### PM Effectiveness

Shows:

- days-to-next-failure distribution
- failure-free probability after PM
- on-time vs delayed PM comparison
- PM delay vs days to next failure

### Failures & Cost

Shows:

- failures by category
- failures by severity
- repair cost by region
- downtime by model
- business impact

### Telemetry Risk

Shows:

- anomaly score vs days since last PM
- anomaly score by PM age bucket
- top risky assets

### Predictive ML & PM Strategy

Shows:

- ML model training
- Logistic Regression vs Random Forest comparison
- confusion matrix
- feature importance
- asset-level risk scoring
- prescriptive PM action plan

### Saved Outputs

Shows saved figures and output tables.

### Data Explorer & Export

Lets users inspect and download filtered dashboard tables.

---

## Run Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the app:

```bash
streamlit run app.py
```

or:

```bash
streamlit run streamlit_app.py
```

Open:

```text
http://localhost:8501
```

---

## Hugging Face Deployment

Recommended deployment mode:

```text
SDK: Docker
Hardware: CPU Basic
```

Required files:

```text
app.py
requirements.txt
Dockerfile
README.md
data/
outputs/
.streamlit/config.toml
```

Example Dockerfile:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
ENV STREAMLIT_SERVER_HEADLESS=true

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

EXPOSE 7860

CMD ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0", "--server.headless=true", "--browser.gatherUsageStats=false"]
```

---

## Snowflake Streamlit Deployment

Recommended files:

```text
streamlit_app.py
environment.yml
snowflake.yml
data/
outputs/
docs/
```

Recommended runtime:

```text
Python version: 3.11
Runtime: warehouse / warehouse legacy
```

Example `environment.yml`:

```yaml
name: generator_pm_streamlit
channels:
  - snowflake
dependencies:
  - streamlit
  - pandas=2.*
  - numpy
  - plotly
  - scikit-learn
  - matplotlib
  - altair
  - pyyaml
  - snowflake-snowpark-python
```

---

## Large CSV Handling on Hugging Face

If using a large CSV with Hugging Face Xet or Git LFS, the dashboard should read the actual resolved file instead of a pointer file.

A pointer file looks like:

```text
version https://git-lfs.github.com/spec/v1
oid sha256:...
size ...
```

If the dashboard shows only 2 rows and 1 column, the app is reading the pointer instead of the actual CSV.

Fix:

- upload the real file using Hugging Face Xet/LFS
- use the Xet-safe version of the app
- restart or factory reboot the Space

---

## Project Outputs

The dashboard can export:

- filtered asset data
- PM events
- failure events
- telemetry data
- raw telemetry
- algorithm output
- latest asset risk summary
- PM-to-failure linked table
- dashboard data ZIP

---

## Limitations

The current version is a proof-of-concept.

Limitations:

- default data is synthetic
- results are not production-validated
- real generator PM and failure data are required for production use
- ML predictions depend on quality of telemetry labels
- business impact numbers are demo estimates
- model monitoring and retraining are needed for production

---

## Production Next Steps

Recommended next steps:

1. Connect real generator asset data.
2. Connect real PM work orders.
3. Connect real failure and repair tickets.
4. Connect telemetry signals.
5. Validate asset IDs and timestamps.
6. Rebuild PM-to-failure links using production data.
7. Retrain ML models on real failure labels.
8. Validate risk scores with maintenance SMEs.
9. Store outputs in Snowflake tables.
10. Add scheduled refresh and alerting.
11. Add model monitoring.
12. Integrate recommendations with work-order systems.

---

## Tech Stack

- Python
- Streamlit
- Pandas
- NumPy
- Plotly
- Scikit-learn
- Matplotlib
- Docker
- Hugging Face Spaces
- Snowflake Streamlit

---

## Repository

```text
https://github.com/dranubhaparashar/Predictive_Preventive_Maintenance_for_Generator_Reliability
```

---

## Author / Maintainer

Built for generator reliability analytics, PM effectiveness measurement, predictive failure-risk modeling, and prescriptive maintenance planning.

---

## License

Add the appropriate license for your organization or repository before production/public release.


## What this package contains
This package upgrades the generator reliability dashboard into a **three-phase ML-based dashboard**.

### Phase 1 - Descriptive / Diagnostic
Uses PM events, failure events, and PM-to-failure linking to show:
- days to next failure after PM,
- on-time PM vs delayed PM comparison,
- failure-free probability after PM,
- failure volume by model.

### Phase 2 - Predictive ML
Uses generator telemetry with labels to train:
- Logistic Regression (baseline)
- Random Forest (advanced)

It predicts:
- `failure_within_14d`
- `failure_within_30d`

### Phase 3 - Prescriptive PM Strategy
Combines:
- reliability history,
- ML risk scores,
- business impact

Outputs:
- prioritized asset action list,
- recommended PM interval guidance,
- cost exposure insight.

## Files
- `streamlit_app.py` - main dashboard app
- `data/` - bundled CSV inputs
- `docs/DASHBOARD_EXPLANATION.md` - dashboard explanation and talking points
- `requirements.txt` - local run dependencies

## Local run
```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```


