#!/usr/bin/env bash
set -euo pipefail

SNOWFLAKE_CONNECTION="${SNOWFLAKE_CONNECTION:-default}"
SNOWFLAKE_ROLE="${SNOWFLAKE_ROLE:-SYSADMIN}"
SNOWFLAKE_DATABASE="${SNOWFLAKE_DATABASE:-GENERATOR_PM_DB}"
SNOWFLAKE_SCHEMA="${SNOWFLAKE_SCHEMA:-PUBLIC}"
SNOWFLAKE_WAREHOUSE="${SNOWFLAKE_WAREHOUSE:-COMPUTE_WH}"

cd "$(dirname "$0")"

echo "Deploying Generator PM Reliability Dashboard to Snowflake Streamlit..."
echo "Connection: $SNOWFLAKE_CONNECTION"
echo "Role: $SNOWFLAKE_ROLE"
echo "Database: $SNOWFLAKE_DATABASE"
echo "Schema: $SNOWFLAKE_SCHEMA"
echo "Warehouse: $SNOWFLAKE_WAREHOUSE"

snow streamlit deploy generator_pm_reliability_dashboard \
  --replace \
  --prune \
  --open \
  --connection "$SNOWFLAKE_CONNECTION" \
  --role "$SNOWFLAKE_ROLE" \
  --database "$SNOWFLAKE_DATABASE" \
  --schema "$SNOWFLAKE_SCHEMA" \
  --warehouse "$SNOWFLAKE_WAREHOUSE"
