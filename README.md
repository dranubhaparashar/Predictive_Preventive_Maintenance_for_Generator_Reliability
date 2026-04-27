# Generator Reliability - 3-Phase ML Streamlit Dashboard

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

## Recommended leadership message
This solution now demonstrates a full analytics maturity path:
**Descriptive -> Predictive -> Prescriptive**.



This folder contains three wiki files:

- `01_TECHNICAL_WIKI.md`
- `02_ARCHITECTURE_WIKI.md`
- `03_FUNCTION_REFERENCE_WIKI.md`

Generated for repository:

```text
https://github.com/dranubhaparashar/Predictive_Preventive_Maintenance_for_Generator_Reliability
```


