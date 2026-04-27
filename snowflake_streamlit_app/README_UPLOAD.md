# Snowflake Streamlit Upload-Ready Files

Upload these files to your Snowflake Streamlit app:

1. `streamlit_app.py`
2. `environment.yml`

Optional if using Snowflake CLI/project deployment:
3. `snowflake.yml`

## Important Snowflake settings

Use:
- Python environment: Run on warehouse / warehouse legacy
- Python version: 3.11 in Packages panel
- Packages from `environment.yml`

Do not use:
- `pyproject.toml`
- `requirements.txt`
- container runtime, unless external PyPI access is configured

## What this version includes

- No specific stakeholder name in dashboard text.
- PM-to-failure analytics.
- Predictive ML & PM Strategy tab.
- Logistic Regression baseline.
- Random Forest advanced model.
- ML model metrics: Accuracy, Precision, Recall, F1, ROC AUC.
- Confusion matrix.
- Feature importance.
- Asset-level ML failure risk.
- Prescriptive maintenance action plan.

## If your app command runs app.py locally

Use:

```bash
cp streamlit_app.py app.py
streamlit run app.py
```

For Snowflake, keep the main file as:

```text
streamlit_app.py
```
