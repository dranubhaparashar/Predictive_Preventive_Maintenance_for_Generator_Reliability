# Predictive Preventive Maintenance for Generator Reliability — Dashboard Dataset & WSL Guide

## Project title

**Predictive Preventive Maintenance for Generator Reliability**

## What this dashboard does

This Streamlit dashboard demonstrates a complete maintenance analytics workflow for generators:

1. Loads the default generator dataset included in the package.
2. Allows the user to upload custom CSV files from the dashboard sidebar.
3. Shows the raw telemetry dataset before any algorithmic enrichment.
4. Applies a transparent risk-scoring algorithm.
5. Shows the processed output after the algorithm.
6. Visualizes PM effectiveness, failure risk, downtime, cost, and business impact.
7. Provides downloadable processed CSV outputs.

## Primary WSL dataset path

Use this raw telemetry file path in WSL:

```bash
/mnt/c/Users/AnubhaAnubha/OneDrive - Pearce Services, LLC/onedrive_ubuntu/project/Predictive_Preventive_Maintenance_for_Generator_Reliability/data/raw/generator_telemetry_with_labels.csv
```

The dashboard first checks this WSL path. If the file exists, it uses this file as the raw telemetry source.

If the file is not found there, it falls back to the packaged raw dataset:

```bash
/mnt/c/Users/AnubhaAnubha/OneDrive - Pearce Services, LLC/onedrive_ubuntu/project/Predictive_Preventive_Maintenance_for_Generator_Reliability/data/raw/generator_telemetry_with_labels.csv
```

When running directly from the downloaded package, the fallback path inside the package is:

```bash
./data/raw/generator_telemetry_with_labels.csv
```

## Recommended WSL project folder

Place or extract the dashboard package here:

```bash
/mnt/c/Users/AnubhaAnubha/OneDrive - Pearce Services, LLC/onedrive_ubuntu/project/Predictive_Preventive_Maintenance_for_Generator_Reliability
```

## Run commands in WSL

```bash
cd "/mnt/c/Users/AnubhaAnubha/OneDrive - Pearce Services, LLC/onedrive_ubuntu/project/Predictive_Preventive_Maintenance_for_Generator_Reliability"
pip install -r requirements.txt
streamlit run app.py
```

If Streamlit is not installed:

```bash
pip install streamlit pandas numpy plotly scikit-learn matplotlib
streamlit run app.py
```

## Dataset files used by the dashboard

### Raw dataset

```bash
/mnt/c/Users/AnubhaAnubha/OneDrive - Pearce Services, LLC/onedrive_ubuntu/project/Predictive_Preventive_Maintenance_for_Generator_Reliability/data/raw/generator_telemetry_with_labels.csv
```

This is the raw telemetry table before the dashboard algorithm enriches it.

Expected important columns:

| Column | Meaning |
|---|---|
| `asset_id` | Generator or asset identifier |
| `timestamp` | Telemetry date/time |
| `age_years` | Asset age in years |
| `days_since_last_pm` | Number of days since the last preventive maintenance |
| `days_to_next_failure` | Number of days until the next known failure, if available |
| `runtime_hours_week` | Weekly runtime hours |
| `avg_load_pct` | Average generator load percentage |
| `oil_temp_c` | Oil temperature |
| `coolant_temp_c` | Coolant temperature |
| `battery_voltage` | Battery voltage |
| `vibration_mm_s` | Vibration measurement |
| `fuel_rate_lph` | Fuel consumption rate |
| `alarm_count` | Alarm count in the period |
| `anomaly_score` | Precomputed anomaly/risk signal |
| `failure_within_30d` | Ground-truth/demo label for failure within 30 days |
| `failure_within_14d` | Ground-truth/demo label for failure within 14 days |
| `model` | Generator model |
| `region` | Region/location grouping |
| `criticality` | Asset criticality |
| `environment_type` | Operating environment |

### Processed datasets

These files are used by the dashboard after preprocessing:

```bash
/mnt/c/Users/AnubhaAnubha/OneDrive - Pearce Services, LLC/onedrive_ubuntu/project/Predictive_Preventive_Maintenance_for_Generator_Reliability/data/processed/asset_master.csv
/mnt/c/Users/AnubhaAnubha/OneDrive - Pearce Services, LLC/onedrive_ubuntu/project/Predictive_Preventive_Maintenance_for_Generator_Reliability/data/processed/pm_events.csv
/mnt/c/Users/AnubhaAnubha/OneDrive - Pearce Services, LLC/onedrive_ubuntu/project/Predictive_Preventive_Maintenance_for_Generator_Reliability/data/processed/failure_events.csv
/mnt/c/Users/AnubhaAnubha/OneDrive - Pearce Services, LLC/onedrive_ubuntu/project/Predictive_Preventive_Maintenance_for_Generator_Reliability/data/processed/pm_failure_linked.csv
/mnt/c/Users/AnubhaAnubha/OneDrive - Pearce Services, LLC/onedrive_ubuntu/project/Predictive_Preventive_Maintenance_for_Generator_Reliability/data/processed/telemetry_weekly.csv
/mnt/c/Users/AnubhaAnubha/OneDrive - Pearce Services, LLC/onedrive_ubuntu/project/Predictive_Preventive_Maintenance_for_Generator_Reliability/data/processed/business_impact.csv
```

## What is shown before the algorithm

The dashboard tab **Dataset & Raw → Algorithm** shows:

1. The exact dataset path being used.
2. Raw row count and column count.
3. Date range.
4. Duplicate-row count.
5. Missing-value count.
6. Raw data preview.
7. Missing-value chart.
8. Raw anomaly-score distribution.
9. Raw signal trend example.

This section answers: **What did the data look like before the algorithm touched it?**

## Algorithm used in the dashboard

The dashboard applies a transparent demo risk-scoring layer:

```text
algorithm_failure_risk_score = 0.75 * anomaly_score + 0.25 * normalized_days_since_last_pm
```

Risk bands:

```text
Low      < 40
Watch    40–59
High     60–79
Critical >= 80
```

Prediction rule:

```text
algorithm_predicted_failure_within_30d = 1 when algorithm_failure_risk_score >= 70
```

Recommended action logic:

| Risk band | Recommended action |
|---|---|
| `Critical` | Immediate inspection / corrective work order |
| `High` | Schedule PM within 7 days |
| `Watch` | Monitor and plan PM |
| `Low` | Normal monitoring |

## What is shown after the algorithm

The dashboard shows:

1. Enriched algorithm output table.
2. `algorithm_failure_risk_score`.
3. `algorithm_risk_band`.
4. `algorithm_predicted_failure_within_30d`.
5. `recommended_action`.
6. Risk-band distribution chart.
7. Predicted 30-day failures by region.
8. Latest asset-level risk summary.
9. Download buttons for algorithm outputs.

This section answers: **What did the algorithm produce from the raw data?**

## PM-to-failure algorithm

For PM effectiveness, the dashboard links preventive maintenance events to later failures:

```text
For each PM event:
    find the first failure event
    where failure.asset_id = pm.asset_id
    and failure.failure_date > pm.pm_date
```

The output table is:

```bash
/mnt/c/Users/AnubhaAnubha/OneDrive - Pearce Services, LLC/onedrive_ubuntu/project/Predictive_Preventive_Maintenance_for_Generator_Reliability/data/processed/pm_failure_linked.csv
```

Important output columns:

| Column | Meaning |
|---|---|
| `pm_event_id` | PM event ID |
| `asset_id` | Generator ID |
| `pm_date` | Date PM was completed |
| `next_failure_event_id` | Next later failure ticket |
| `next_failure_date` | Date of next later failure |
| `days_to_next_failure` | Number of days the asset ran after PM before failing |
| `failure_found_flag` | Whether a later failure was found |
| `ontime_flag` | Whether PM was on-time |
| `delay_days` | How late the PM was |
| `pm_total_cost` | PM cost |
| `failure_total_cost` | Failure repair cost |
| `failure_category` | Failure type |

## Dashboard tabs

| Tab | Purpose |
|---|---|
| Problem & Solution | Explains the business problem and proposed solution |
| Dataset & Raw → Algorithm | Shows dataset path, raw data, algorithm logic, and processed output |
| Executive KPIs | Shows high-level PM, failure, downtime, cost, and impact metrics |
| PM Effectiveness | Shows PM-to-next-failure distribution and survival-style curves |
| Failures & Cost | Shows failure categories, severity, repair cost, downtime, and business impact |
| Telemetry Risk | Shows anomaly/risk patterns from telemetry |
| Saved Outputs | Shows pre-generated plots and output tables |
| Data Explorer & Export | Lets the user inspect and download any loaded table |

## Uploading your own data

In the dashboard sidebar, choose:

```text
Upload my own CSVs / ZIP
```

You can upload:

```bash
asset_master.csv
pm_events.csv
failure_events.csv
pm_failure_linked.csv
telemetry_weekly.csv
business_impact.csv
generator_telemetry_with_labels.csv
```

Minimum required for PM-to-failure analysis:

```bash
pm_events.csv
failure_events.csv
```

Minimum columns:

`pm_events.csv`

```csv
pm_event_id,asset_id,pm_date
```

`failure_events.csv`

```csv
failure_event_id,asset_id,failure_date
```

## Output downloads from dashboard

The dashboard can download:

```bash
algorithm_output.csv
latest_asset_risk_summary.csv
filtered_generator_pm_dashboard_data.zip
```

These are useful for Excel, Power BI, client presentation, or further modeling.

## Business explanation

The dashboard is designed to answer the client question:

> After a preventive maintenance event is completed, how long does the generator operate before the next failure?

It also expands the answer into business value:

- Which generators are risky?
- Which PMs are effective?
- Which failures cost the most?
- Which regions have higher risk?
- Which assets should be inspected first?
- How much downtime and revenue loss is associated with failure events?

## Important note

The included dataset is a large demo/synthetic dataset designed to match the structure of generator preventive maintenance and telemetry data. For client-facing final results, replace the packaged demo CSVs with actual internal PM, repair-ticket, asset-master, telemetry, and business-impact data.
