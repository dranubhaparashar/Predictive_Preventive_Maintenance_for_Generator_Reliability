# Data dictionary

## asset_master.csv
- `asset_id`: unique asset key
- `asset_name`: friendly display name
- `asset_type`: asset category
- `manufacturer`: manufacturer name
- `model`: model name
- `install_date`: installation date
- `location`: site identifier
- `region`: region grouping
- `criticality`: High, Medium, or Low
- `environment_type`: environment label
- `service_interval_days`: nominal PM interval
- `base_runtime_hours_per_week`: baseline weekly runtime
- `base_load_pct`: baseline load percentage

## pm_events.csv
- `pm_event_id`: unique PM event key
- `asset_id`: asset key
- `scheduled_date`: planned PM date
- `completed_date`: actual PM completion date
- `pm_date`: same as completion date
- `pm_type`: PM type
- `status`: PM status
- `delay_days`: completion delay in days
- `ontime_flag`: 1 if PM was on time
- `priority`: PM priority
- `labor_hours`, `labor_cost`, `material_cost`, `other_costs`, `total_cost`
- `age_years_at_pm`: asset age at PM
- `region`, `environment_type`, `model`: inherited context fields

## failure_events.csv
- `failure_event_id`: unique failure key
- `asset_id`: asset key
- `pm_event_id_context`: PM cycle context
- `failure_date`: failure date
- `ticket_open_date`, `ticket_close_date`
- `failure_category`: component or failure type
- `severity`: Low, Medium, High, or Critical
- `priority`: event priority
- `description`: short text
- `downtime_hours`: outage duration
- `labor_hours`, `labor_cost`, `material_cost`, `other_costs`, `total_cost`
- `root_cause`: synthetic root cause
- `region`, `environment_type`, `model`

## pm_failure_linked.csv
- `pm_event_id`: PM event
- `asset_id`: asset key
- `pm_date`: PM completion date
- `next_failure_event_id`: first later failure for same asset
- `next_failure_date`: date of first later failure
- `days_to_next_failure`: PM-to-failure duration
- `failure_found_flag`: 1 if later failure exists
- `ontime_flag`: copied from PM table
- `delay_days`: PM delay
- `pm_total_cost`: PM cost
- `failure_total_cost`: linked failure cost
- `failure_category`: linked failure type

## telemetry_weekly.csv
- `asset_id`
- `timestamp`
- `age_years`
- `days_since_last_pm`
- `days_to_next_failure`
- `runtime_hours_week`
- `avg_load_pct`
- `oil_temp_c`
- `coolant_temp_c`
- `battery_voltage`
- `vibration_mm_s`
- `fuel_rate_lph`
- `alarm_count`
- `anomaly_score`
- `failure_within_30d`
- `failure_within_14d`

## business_impact.csv
- `asset_id`
- `failure_event_id`
- `event_date`
- `downtime_hours`
- `truck_roll_cost`
- `repair_cost`
- `estimated_customers_impacted`
- `estimated_revenue_loss`
- `sla_breach_flag`
- `notes`
