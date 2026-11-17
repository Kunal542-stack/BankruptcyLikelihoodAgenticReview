# New XGBoost Model (2009 to 2026)

The bigger version of our model: more years, more features from the 10-K and 10-Q filings, the late filing notices (NT 10-K, NT 10-Q), and calibrated probabilities. The probabilities are in `agent/shared/risk_scores_calibrated.csv`.

## Files, in the order they run

1. `collect_data.ipynb`: downloads the SEC Financial Statement Data Sets (2009 Q1 to 2026 Q3) and the SEC full text search results (bankruptcy 8-Ks for the labels, late filing notices, warning phrases in 10-Ks and 10-Qs) into `data/`.
2. `build_dataframe.ipynb`: one row per 10-K or 10-Q, the labels and the 130 features. Saves `model_dataframe_2009_to_2026.pkl`.
3. `xgboost_model.ipynb`: the walk forward test, the calibration (isotonic or Platt, whichever has the lower log loss) and the CSV for the agent.

The SEC asks for a name and email with every request, so set it before starting Jupyter:

```bash
export SEC_USER_AGENT="Your Name your.email@school.edu"
```

The data and the `.pkl` file are not in the repo (too big). Running 1 and 2 rebuilds them.

## The test

Walk forward by year: the reports of each two test years are scored by a model trained on reports filed 2 or more years before, so their answers were already known. Nothing from after the report is used for its features.

## Results (Platt calibration was kept)

| Test years | Brier | Log loss | PR-AUC | ROC-AUC |
|---|---|---|---|---|
| 2016 to 2021 | 0.0067 | 0.0328 | 0.158 | 0.885 |
| 2023 to 2025 | 0.0086 | 0.039 | 0.148 | 0.911 |

Under 1% of reports are followed by a bankruptcy (0.7% in 2016 to 2021), so a random model has a PR-AUC of about 0.007.
