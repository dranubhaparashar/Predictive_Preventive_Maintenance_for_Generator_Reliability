-- Snowflake CLI deployment is recommended for this package.
-- If using SQL/PUT manually, run PUT commands from SnowSQL/Snowflake CLI, not a standard worksheet.
-- Example pattern only; update local paths before use:

-- CREATE STAGE IF NOT EXISTS GENERATOR_PM_DB.PUBLIC.GENERATOR_PM_STREAMLIT_STAGE;
-- PUT file:///absolute/path/to/streamlit_app.py @GENERATOR_PM_DB.PUBLIC.GENERATOR_PM_STREAMLIT_STAGE/app AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
-- PUT file:///absolute/path/to/environment.yml @GENERATOR_PM_DB.PUBLIC.GENERATOR_PM_STREAMLIT_STAGE/app AUTO_COMPRESS=FALSE OVERWRITE=TRUE;

-- Then create the Streamlit object. Newer Snowflake syntax uses FROM source_location.
-- Exact syntax can depend on account/runtime version, so Snowflake CLI is safer.
