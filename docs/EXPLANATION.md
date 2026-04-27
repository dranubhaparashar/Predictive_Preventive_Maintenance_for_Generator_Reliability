# Explanation and design notes

## Why this package exists

This package is built for a quick predictive maintenance demo focused on a generator use case.  
It is especially useful when you need to show the workflow before internal client data is available.

## What the data represents

### asset_master.csv
One row per generator asset.

### pm_events.csv
A preventive maintenance log with:
- scheduled date
- completion date
- delay days
- PM type
- labor and material cost

### failure_events.csv
A corrective maintenance or failure log with:
- failure date
- severity
- downtime
- repair cost
- root cause

### pm_failure_linked.csv
A derived table that links every PM event to the **first later failure** for the same asset.

This is the most important table if your goal is to answer:
> How long does a generator remain failure-free after PM?

### telemetry_weekly.csv
Weekly sensor-style aggregates with:
- temperatures
- battery voltage
- vibration
- fuel rate
- alarm count
- anomaly score
- labels for failure within 14 and 30 days

### business_impact.csv
Synthetic estimates for:
- downtime
- truck roll cost
- repair cost
- customers impacted
- revenue loss
- SLA breach indicator

## How the synthetic data was designed

The package simulates:
- generator fleets with different models, ages, regions, and environments
- preventive maintenance intervals
- PM delays
- higher failure likelihood for older assets, delayed PM, and harsher environments
- telemetry drift as assets move closer to failure

This means the demo produces realistic analysis patterns:
- on-time PM usually leads to more failure-free days
- delayed PM usually shortens the time to the next failure
- rising vibration and falling battery voltage often appear before failure
- failures create business impact through downtime and cost

## What each notebook does

## 01_data_overview.ipynb
Loads all tables and checks the shapes, columns, and basic quality.

## 02_pm_to_failure_analysis.ipynb
Rebuilds the PM-to-next-failure linkage from the raw tables and compares:
- on-time vs delayed PM
- histogram of days to next failure
- failure-free probability curve

## 03_telemetry_risk_model.ipynb
Trains a baseline Random Forest model to predict `failure_within_30d` from telemetry features.

## 04_business_impact_and_exports.ipynb
Summarizes:
- operational KPIs
- business cost
- top-risk assets
- regional revenue loss

## How to adapt this package to real data

Replace these files first:
- `asset_master.csv`
- `pm_events.csv`
- `failure_events.csv`
- `telemetry_weekly.csv`

Keep the same column names whenever possible.  
Then rerun the notebooks.

## Recommended real-world join keys

Use one stable asset key:
- `generator_id`
or
- `site_id + generator_id`

Without a stable key, PM-to-failure linkage will be messy and error-prone.

## Recommended next steps

1. Replace the synthetic PM and failure data with internal work orders and repair tickets.
2. Add true telemetry if you have it.
3. Calibrate business impact using actual customer and SLA numbers.
4. Swap the baseline model with your preferred production model.
