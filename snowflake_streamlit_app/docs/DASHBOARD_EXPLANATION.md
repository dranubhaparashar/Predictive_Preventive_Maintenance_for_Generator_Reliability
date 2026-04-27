# Dashboard Explanation

## Problem statement

Generator failures can create site outages, emergency repair costs, SLA breaches, and poor customer experience. The business wants to know whether preventive maintenance is reducing this risk.

The core question is:

> For every completed preventive maintenance event, how many days pass before the next generator failure or repair ticket?

## Solution approach

The dashboard solves this by building a PM-to-failure analytics layer.

### Step 1: Ingest data

The dashboard accepts default demo data or user-uploaded CSV files:

- `asset_master.csv`
- `pm_events.csv`
- `failure_events.csv`
- `business_impact.csv`
- `telemetry_weekly.csv`
- `pm_failure_linked.csv`

### Step 2: Link PM events to future failures

For every PM event:

```text
Find the first failure for the same asset where failure_date > pm_date
```

This creates:

```text
days_to_next_failure = next_failure_date - pm_date
```

### Step 3: Measure PM effectiveness

The dashboard calculates:

- Average days from PM to next failure
- Median days from PM to next failure
- Failure within 30 days
- Failure within 90 days
- On-time PM vs delayed PM comparison
- Failure-free probability curve

### Step 4: Analyze failure impact

The dashboard summarizes:

- Failure categories
- Severity mix
- Downtime hours
- Repair cost
- Truck-roll cost
- Revenue loss
- Estimated customers impacted
- SLA breach count

### Step 5: Add telemetry risk

The telemetry tab visualizes:

- Anomaly score
- Days since last PM
- Failure-within-30-days label
- Highest-risk assets

## Business value

This dashboard helps answer:

- Which generators are failing soon after PM?
- Are delayed PMs linked to higher failure risk?
- Which models or regions create the most downtime?
- Which assets should be prioritized for service?
- What is the estimated cost and customer impact of generator failures?

## Recommended production data

For a real deployment, use:

1. Preventive maintenance records
2. Corrective repair/failure tickets
3. Generator asset master
4. Telemetry/runtime data
5. Outage/customer/business impact data

## Demo limitation

The included dataset is synthetic and intended for demonstration. Replace it with internal generator data for client-specific recommendations.
