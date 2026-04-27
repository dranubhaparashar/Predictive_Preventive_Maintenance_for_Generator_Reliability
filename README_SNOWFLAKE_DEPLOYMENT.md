# Generator PM Reliability Dashboard — Snowflake Streamlit Deployment

This folder is a Snowflake Streamlit-ready version of the **Predictive Preventive Maintenance for Generator Reliability** dashboard.

It includes:

- `streamlit_app.py` — Snowflake Streamlit entrypoint
- `snowflake.yml` — Snowflake CLI project definition
- `environment.yml` — Snowflake package environment
- `data/` — packaged default generator PM demo dataset
- `outputs/` — generated KPI tables and figures
- `docs/` — explanation, data dictionary, and WSL guide
- `deploy_snowflake_from_wsl.sh` — WSL deployment helper
- `sql/00_create_database_schema_stage.sql` — optional Snowflake setup script

---

## Important

I cannot directly upload to your Snowflake account from ChatGPT because I do not have your Snowflake credentials, role, database, schema, warehouse, or network access.

This package is ready for **you or Anubha** to deploy from WSL using Snowflake CLI.

---

## WSL project path

Recommended folder location in WSL:

```bash
/mnt/c/Users/AnubhaAnubha/OneDrive\ -\ Pearce\ Services,\ LLC/onedrive_ubuntu/project/Predictive_Preventive_Maintenance_for_Generator_Reliability/snowflake_streamlit_app
```

If you unzip this package elsewhere, use that folder path in the commands below.

---

## Step 1: Install Snowflake CLI in WSL

```bash
python3 -m pip install --upgrade snowflake-cli
snow --version
```

---

## Step 2: Configure Snowflake connection

Run:

```bash
snow connection add
```

Give it a connection name such as:

```text
default
```

Then test:

```bash
snow connection test --connection default
```

---

## Step 3: Create database, schema, warehouse, and stage

Open Snowsight SQL Worksheet and run:

```sql
USE ROLE SYSADMIN;

CREATE WAREHOUSE IF NOT EXISTS COMPUTE_WH
  WAREHOUSE_SIZE = XSMALL
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE;

CREATE DATABASE IF NOT EXISTS GENERATOR_PM_DB;
CREATE SCHEMA IF NOT EXISTS GENERATOR_PM_DB.PUBLIC;
CREATE STAGE IF NOT EXISTS GENERATOR_PM_DB.PUBLIC.GENERATOR_PM_STREAMLIT_STAGE;
```

If your company uses a different warehouse/database/schema, update `snowflake.yml` and the deploy command accordingly.

---

## Step 4: Deploy from WSL

Go to the package folder:

```bash
cd "/mnt/c/Users/AnubhaAnubha/OneDrive - Pearce Services, LLC/onedrive_ubuntu/project/Predictive_Preventive_Maintenance_for_Generator_Reliability/snowflake_streamlit_app"
```

Deploy:

```bash
snow streamlit deploy generator_pm_reliability_dashboard \
  --replace \
  --prune \
  --open \
  --connection default \
  --role SYSADMIN \
  --database GENERATOR_PM_DB \
  --schema PUBLIC \
  --warehouse COMPUTE_WH
```

Or run the helper script:

```bash
chmod +x deploy_snowflake_from_wsl.sh
./deploy_snowflake_from_wsl.sh
```

---

## Step 5: Open the app

If `--open` works, the browser opens automatically.

Otherwise, get the app URL:

```bash
snow streamlit get-url generator_pm_reliability_dashboard \
  --connection default \
  --database GENERATOR_PM_DB \
  --schema PUBLIC
```

---

## What the dashboard shows

### 1. Problem & Solution
Explains the maintenance problem:

> After preventive maintenance is completed, how long does a generator typically run before the next failure or repair ticket?

It also explains the solution:

- load PM and failure data
- link each PM to the next failure
- compute days-to-next-failure
- compare on-time vs delayed PM
- show telemetry-based risk
- estimate downtime and business impact

### 2. Dataset & Raw → Algorithm
Shows:

- dataset used
- raw telemetry source path
- raw dataset preview
- raw missing-value chart
- raw anomaly signals
- algorithm-enriched output
- risk bands
- predicted 30-day failures

### 3. Executive KPIs
Shows:

- total assets
- total PMs
- total failures
- median days to next failure
- total downtime
- total estimated cost

### 4. PM Effectiveness
Shows:

- PM-to-next-failure distribution
- survival-style failure-free curve
- on-time vs delayed PM comparison

### 5. Failures & Cost
Shows:

- repair cost
- downtime
- failure categories
- impact by region/model

### 6. Telemetry Risk
Shows:

- anomaly score
- risk bands
- high-risk assets
- sensor/risk visualizations

### 7. Saved Outputs
Shows prebuilt KPI and asset summary outputs.

### 8. Data Explorer & Export
Lets users inspect and download processed tables.

---

## Files included for Snowflake deployment

```text
snowflake_streamlit_app/
├── streamlit_app.py
├── snowflake.yml
├── environment.yml
├── deploy_snowflake_from_wsl.sh
├── README_SNOWFLAKE_DEPLOYMENT.md
├── sql/
│   ├── 00_create_database_schema_stage.sql
│   └── 01_manual_stage_and_create_streamlit_notes.sql
├── data/
│   ├── raw/
│   │   └── generator_telemetry_with_labels.csv
│   └── processed/
│       ├── asset_master.csv
│       ├── pm_events.csv
│       ├── failure_events.csv
│       ├── business_impact.csv
│       ├── pm_failure_linked.csv
│       └── telemetry_weekly.csv
├── outputs/
│   ├── figures/
│   └── tables/
└── docs/
```

---

## Notes for Snowflake Streamlit

- This version uses `streamlit_app.py` because Snowflake CLI expects that as the default main file.
- The app reads packaged CSVs from the deployed app directory.
- The original WSL path is displayed in the dashboard for documentation, but Snowflake will use the packaged data files because Snowflake cannot access your local `/mnt/c/...` path after deployment.
- Upload mode is still available inside the dashboard for custom CSV or ZIP inputs.
- No secret keys are included.

---

## Quick troubleshooting

### Error: warehouse does not exist
Update `query_warehouse` in `snowflake.yml` and the `--warehouse` flag.

### Error: insufficient privileges
Ask your Snowflake admin for privileges to:

- use role
- use warehouse
- create/use database
- create/use schema
- create/use stage
- create Streamlit app

### Error: package not found
Remove the package from `environment.yml` or ask admin to enable Snowflake Anaconda packages.

### App runs but data is missing
Make sure the `data/` folder was included in deployment. The package’s `snowflake.yml` includes `data/**/*` as deploy artifacts.
