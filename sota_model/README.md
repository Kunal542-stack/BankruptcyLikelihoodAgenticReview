# New XGBoost Model (2009 to 2026)

The bigger version of our model: more years, more features from the 10-K and 10-Q filings, the late filing notices, and calibrated probabilities. The probabilities are in `agent/shared/risk_scores_calibrated.csv`.

## Files, in the order they run

1. `download_zips.sh`: the SEC Financial Statement Data Sets for 2009 to 2022 into `data/zips/` (5.6 GB). The 2023+ ones are the same files we already use.
2. `collect_efts.py`: SEC full text search, one month at a time from 2007 to 2026, saved in `data/efts/`. It gets the bankruptcy 8-Ks (Item 1.03, for the labels), the late filing notices (NT 10-K, NT 10-Q), and the 10-Ks and 10-Qs that have phrases like "substantial doubt" + "going concern" or "forbearance agreement". (It also gets some warning 8-Ks, which the final model doesn't use.)
3. `build_long_dataframe.ipynb`: one row per 10-K or 10-Q from 2009 to 2026 (388,251 rows), the labels, and the features. Saves `long_dataframe_2009_to_2026.pkl` and `feature_groups.json`.
4. `sota_model.ipynb`: the tests we used to pick the features and the model (walk forward by year, other models, the tuning).
5. `text_model.ipynb`: the test of the MD&A text. It didn't change the PR-AUC, so the final model doesn't use it.
6. `final_model.ipynb`: the model we keep, the calibration, and the CSV for the agent.

The data and the `.pkl` file are not in the repo (too big). Running 1 to 3 rebuilds them.

## The test

Walk forward by year: the reports of each test year are scored by a model trained on reports filed 2 or more years before, so their answers were already known. Nothing from after the report is used for its features: 8-Ks and notices only count if filed on or before the report date.

## Results

Same walk forward test on two windows.

| Test | Model | PR-AUC | ROC-AUC |
|---|---|---|---|
| 2016 to 2021, 10-K only (the test of Arno et al., 2023) | final model | 0.158 | 0.885 |
| | Arno et al., numbers only | 0.156 | 0.936 |
| | Arno et al., numbers + MD&A text | 0.264 | 0.948 |
| 2023 to 2025, all reports (our years) | final model | 0.148 | 0.911 |

The 2016 to 2021 row of the final model is for all reports of those years. The 10-K only number in `text_model.ipynb` ("+ NT") is 0.157.

**Calibration.** Isotonic and Platt gave the same Brier score (0.0067 on 2016 to 2021), but isotonic lowered the PR-AUC (0.147) because its steps give many reports the same probability. Platt kept the order (PR-AUC 0.158) and had the lower log loss (0.0328 against 0.0331), so the final model uses Platt.

After calibration the probabilities match what happened: of the reports given 20% to 50%, 24% went bankrupt within a year (the raw score for them was 34% on average).

## The CSV for the agent

`agent/shared/risk_scores_calibrated.csv`, sorted from the highest probability:
- 63,767 reports filed 2023 to 2025 (answer known): probability from the walk forward, from a model that never saw them.
- 21,986 newer reports (answer not known yet): a model trained on every report with a known answer.

Columns: `adsh, cik, name, form, ddate, filed, probability` (calibrated), `raw_score` (before calibration), `scored_by`.
