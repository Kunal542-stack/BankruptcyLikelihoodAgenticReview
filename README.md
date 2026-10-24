# Agentic Framework for Bankruptcy Likelihood and Explanation

**DS 5500 Capstone, Northeastern University**

**Authors:** Kunal Deb, Pavanchytanya Dharmapuri, Pramukh Venkatesh Koushik
**Sponsors:** Kunal Deb, Kylie Bemis, Pavanchytanya Dharmapuri, Pramukh Venkatesh Koushik

## Abstract

Many companies keep operating while they ignore financial problems until it is too late, and the bankruptcy that follows hurts the people who work there. Bankruptcy is nuanced, so knowing *why* a company is at risk matters as much as knowing *that* it is. We are building a pipeline that, for companies with a high likelihood of bankruptcy, explains what is causing it. The pipeline has two layers. In the ML layer, we use the SEC Financial Statement Data Sets to build company variables such as revenue and liabilities, use 8-K filings to find which companies declared bankruptcy, and train an XGBoost classifier that gives each quarterly or annual report a probability of bankruptcy within a year. Using filings from 2023 to 2025, the model reaches a ROC-AUC of about 0.896. In the agentic layer, an investigator agent researches why a high-risk company looks the way it does and writes a report, and a reviewer agent checks that report. A basic version of the investigator agent has been built; the reviewer agent is planned.

## Pipeline

```
SEC Financial Statement Data Sets (2023 Q1 – 2026 Q3)      EDGAR full-text search: 8-K Item 1.03
                 │                                                       │
                 └────────────── build_dataframe.ipynb ─────────────────┘
                                         │
                        model_dataframe_2023_Q1_to_2026_Q3.txt
                                         │
                                xgboost_model.ipynb
                                         │
                agent/shared/financials.csv + agent/shared/risk_scores.csv
                                         │
                     agent/investigator_agent.py  →  agent/cases/<adsh>/report.md
                                         │
                            reviewer agent (planned)
```

## Repository layout

| Path | What it is |
|---|---|
| `build_dataframe.ipynb` | Builds the dataframe the model reads: one row per 10-K or 10-Q, the 8 variables and the bankruptcy label |
| `xgboost_model.ipynb` | Trains and tests the XGBoost model, and saves the files the agent reads |
| `agent/investigator_agent.py` | The investigator agent (Claude Agent SDK, Claude Opus 5.5) |
| `agent/sec_tools.py` | Tools the agent uses to list and download a company's SEC filings |
| `agent/shared/financials.csv` | Every report's 8 variables, without the labels (made by `xgboost_model.ipynb`) |
| `agent/shared/risk_scores.csv` | The model's probability for the test reports (made by `xgboost_model.ipynb`) |
| `agent/cases/<adsh>/` | Created when the agent runs: its `report.md`, charts and scripts for each report (not in the repository) |
| `requirements.txt` | Python packages |

The SEC data (`data/`) and the dataframe file are not in the repository because of their size. `build_dataframe.ipynb` rebuilds the dataframe from the SEC files.

## Data

| Source | Used for |
|---|---|
| [SEC Financial Statement Data Sets](https://www.sec.gov/data-research/sec-markets-data/financial-statement-data-sets), 2023 Q1 – 2026 Q3 (`sub` and `num` tables) | The 8 variables |
| [EDGAR full-text search](https://www.sec.gov/edgar/search/), 8-Ks with Item 1.03 (Bankruptcy or Receivership), 2021 – 2026 | The bankruptcy labels |

**Variables** (company-level totals in US dollars; income and cash flow on a 12-month basis):

| Variable | SEC tag | Backup tag |
|---|---|---|
| total_assets | Assets | – |
| current_assets | AssetsCurrent | – |
| current_liabilities | LiabilitiesCurrent | – |
| total_liabilities | Liabilities | LiabilitiesAndStockholdersEquity − StockholdersEquity |
| revenue | RevenueFromContractWithCustomerExcludingAssessedTax | Revenues, RevenueFromContractWithCustomerIncludingAssessedTax, SalesRevenueNet |
| net_income | NetIncomeLoss | ProfitLoss |
| operating_income | OperatingIncomeLoss | – |
| operating_cash_flow | NetCashProvidedByUsedInOperatingActivities | NetCashProvidedByUsedInOperatingActivitiesContinuingOperations |

**Label:** `Bankruptcy = 1` if the company filed a bankruptcy 8-K (Item 1.03) within 365 days after the report. Reports filed less than a year before the label date (Oct 17, 2026) have no known answer yet and are not used for training. Reports from companies that were already bankrupt when they filed are also left out.

| Step | Rows |
|---|---|
| One row per filing | 101,001 |
| 10-K and 10-Q only | 88,674 |
| One filing per company and period | 86,927 |
| Rows to train on | 64,537 (609 followed by a bankruptcy, 63,928 not) |

## Model

- **XGBoost** with class weighting for the imbalance (about 1% of reports are followed by a bankruptcy). Missing values are left empty; XGBoost handles them directly.
- **Split by company and by time.** Companies are put into 4 groups. In each of 4 rounds, the model is trained on the earlier half-year blocks of 3 groups and tested on the next half-year of the 4th group, so it is never tested on a company it was trained on, and it is always tested on filings that come after the ones it trained on.
- **Optuna** (40 trials per round) tunes the settings inside each round's training part, using 4-fold cross-validation split by company.

| Round | Train on | Test on | ROC-AUC |
|---|---|---|---|
| 1 | 2023 H1 | 2023 H2 | 0.947 |
| 2 | 2023 H1 – H2 | 2024 H1 | 0.880 |
| 3 | 2023 H1 – 2024 H1 | 2024 H2 | 0.927 |
| 4 | 2023 H1 – 2024 H2 | 2025 | 0.828 |
| **Average** | | | **0.896 ± 0.053** |

Net income is the most important variable, followed by operating income and operating cash flow.

## Investigator agent

The agent gets one report and the model's probability, and works out why the probability is what it is. It reads the company's numbers in `agent/shared/financials.csv`, downloads and reads its SEC filings with `sec_tools.py`, compares it with industry peers, makes charts, and writes `cases/<adsh>/report.md`. It may only use information filed on or before the report's filing date.

The agent is built with the Claude Agent SDK. Once its prompt produces reports that match our gold standard, the plan is to turn its steps into a LangGraph workflow, which is more fixed and deterministic. A reviewer agent that checks the investigator's reports comes after that.

## How to run

1. Install the packages:
   ```bash
   pip install -r requirements.txt
   ```
2. Download the SEC Financial Statement Data Sets for 2023 Q1 to 2026 Q3 and unzip each quarter into `data/<year>Q<n>/`, for example `data/2023Q1/sub.txt` and `data/2023Q1/num.txt`.
3. Run `build_dataframe.ipynb`. It writes `model_dataframe_2023_Q1_to_2026_Q3.txt`. SEC asks for a name and email in the `User-Agent` header, so set `HEADERS` to your own.
4. Run `xgboost_model.ipynb`. It prints the results above and writes `agent/shared/financials.csv` and `agent/shared/risk_scores.csv`.
5. Run the agent from the `agent/` folder (it needs Claude Code to be signed in, or `ANTHROPIC_API_KEY` set):
   ```bash
   cd agent
   python investigator_agent.py
   ```
   `PYTHON` at the top of `investigator_agent.py` is the Python the agent uses to run its scripts; point it to an environment with pandas, matplotlib, requests and BeautifulSoup.

## References

1. U.S. Securities and Exchange Commission. *Financial Statement Data Sets*. https://www.sec.gov/data-research/sec-markets-data/financial-statement-data-sets
2. U.S. Securities and Exchange Commission. *EDGAR Full Text Search*. https://www.sec.gov/edgar/search/
3. Chen, T., and Guestrin, C. "XGBoost: A Scalable Tree Boosting System." *KDD*, 2016.
4. Akiba, T., et al. "Optuna: A Next-generation Hyperparameter Optimization Framework." *KDD*, 2019.
