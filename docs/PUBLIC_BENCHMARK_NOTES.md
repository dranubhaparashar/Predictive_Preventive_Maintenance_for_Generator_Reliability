# Public benchmark notes

This package includes a large synthetic demo dataset because the container used to build the package could not reliably pull the public benchmark files directly.

To help you extend this package on your machine, here are the benchmark sources used as the design reference:

## Public benchmarks used as references
- UCI AI4I 2020 Predictive Maintenance Dataset
- NASA C-MAPSS Jet Engine Simulated Data
- FMUCD building maintenance dataset for planned preventive and unplanned maintenance

## How these benchmarks inspired the package
- AI4I inspired the idea of clean failure labels and machine-health features.
- C-MAPSS inspired the telemetry-to-failure pattern and remaining-life logic.
- FMUCD inspired the PM-event and failure-event workflow.

## Downloader script
Use `scripts/download_public_benchmarks.py` if you want to fetch public benchmark files directly on your own machine.
