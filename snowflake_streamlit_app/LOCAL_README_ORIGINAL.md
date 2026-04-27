# Generator PM Reliability Streamlit Dashboard

This package contains a complete dashboard for analyzing generator preventive maintenance effectiveness.

## What the dashboard does

It answers the core business question:

> After a preventive maintenance event is completed, how long does the generator run before the next failure or repair ticket?

The dashboard supports:

- Default included demo dataset
- Custom CSV uploads
- ZIP upload with all required CSVs
- PM-to-next-failure linking
- KPI cards
- PM effectiveness charts
- Failure category, downtime, and cost analysis
- Telemetry/anomaly risk visualization
- Business impact summary
- Export of filtered dashboard data

## Folder structure

```text
generator_pm_streamlit_dashboard/
├── app.py
├── requirements.txt
├── README.md
├── run_dashboard.bat
├── run_dashboard.sh
├── data/
│   └── processed/
│       ├── asset_master.csv
│       ├── pm_events.csv
│       ├── failure_events.csv
│       ├── business_impact.csv
│       ├── pm_failure_linked.csv
│       └── telemetry_weekly.csv
├── notebooks/
├── outputs/
└── docs/
```

## How to run

### Option 1: Windows

Open PowerShell or Command Prompt inside this folder:

```bash
pip install -r requirements.txt
streamlit run app.py
```

Or double-click / run:

```bash
run_dashboard.bat
```

### Option 2: Mac / Linux

```bash
pip install -r requirements.txt
streamlit run app.py
```

Or:

```bash
bash run_dashboard.sh
```

## Upload your own data

You can upload either:

1. A ZIP file containing CSVs with these names:
   - `asset_master.csv`
   - `pm_events.csv`
   - `failure_events.csv`
   - `business_impact.csv`
   - `pm_failure_linked.csv`
   - `telemetry_weekly.csv`

2. Individual CSVs from the sidebar.

Minimum required files for PM-to-failure analysis:

- `pm_events.csv`
- `failure_events.csv`

Required columns:

### `pm_events.csv`

```csv
pm_event_id,asset_id,pm_date
```

Optional but recommended:

```csv
scheduled_date,completed_date,pm_type,status,delay_days,ontime_flag,total_cost,region,environment_type,model
```

### `failure_events.csv`

```csv
failure_event_id,asset_id,failure_date
```

Optional but recommended:

```csv
failure_category,severity,downtime_hours,total_cost,root_cause,region,environment_type,model
```

The dashboard can automatically rebuild `pm_failure_linked.csv` from PM and failure records.

## Main dashboard tabs

1. **Problem & Solution**
   - Explains the business problem and dashboard workflow.

2. **Executive KPIs**
   - Shows average days from PM to next failure, downtime, cost, and customer impact.

3. **PM Effectiveness**
   - Shows days-to-failure histogram, failure-free curve, and delayed vs on-time PM comparison.

4. **Failures & Cost**
   - Shows failures by category, severity, region, model, repair cost, and revenue loss.

5. **Telemetry Risk**
   - Shows anomaly score and days-since-last-PM risk patterns.

6. **Saved Outputs**
   - Displays the pre-generated notebook figures and output tables.

7. **Data Explorer & Export**
   - Lets you view and download filtered tables.

## Important note

The included dataset is synthetic and demo-ready. It is designed to show the workflow for generator preventive maintenance reliability analysis. For production/client use, replace the demo data with internal generator PM records, repair tickets, asset master data, telemetry, and business impact data.

## Updated dataset + WSL behavior

The dashboard now includes a dedicated **Dataset & Raw → Algorithm** tab.

It first looks for the raw telemetry dataset at this WSL path:

```bash
/mnt/c/Users/AnubhaAnubha/OneDrive - Pearce Services, LLC/onedrive_ubuntu/project/Predictive_Preventive_Maintenance_for_Generator_Reliability/data/raw/generator_telemetry_with_labels.csv
```

If that file is not present, it falls back to the included package file:

```bash
./data/raw/generator_telemetry_with_labels.csv
```

Run in WSL:

```bash
cd "/mnt/c/Users/AnubhaAnubha/OneDrive - Pearce Services, LLC/onedrive_ubuntu/project/Predictive_Preventive_Maintenance_for_Generator_Reliability"
pip install -r requirements.txt
streamlit run app.py
```

Inside the dashboard, the **Dataset & Raw → Algorithm** tab shows:

- exact dataset path used,
- raw telemetry preview before algorithm,
- raw missing-value visualization,
- raw signal distributions,
- algorithm formula and explanation,
- enriched algorithm output after scoring,
- risk-band distribution,
- predicted 30-day failures by region,
- downloadable `algorithm_output.csv`,
- downloadable `latest_asset_risk_summary.csv`.

See full guide:

```bash
docs/DASHBOARD_DATASET_AND_WSL_GUIDE.md
```
