# Feature Sources: Where Each of the 130 Features Comes From

Saved 2026-11-21. The model is `BankruptcyLikelihoodAgenticReview/sota_model/xgboost_model.ipynb` (XGBoost, 130 features, Platt calibration). All features are built from SEC EDGAR data only: the Financial Statement Data Sets (`num.txt`, `sub.txt`) and EDGAR full-text search.

## Status meanings

- **Exact**: the paper uses the same variable (or the same phrase) as a bankruptcy / distress predictor.
- **Inspired**: the paper uses a close variant or shows the event signals distress, but not our exact variable.
- **Ours**: no paper found.

## Totals

| Exact | Inspired | Ours | Total |
|---|---|---|---|
| 43 | 84 | 3 | 130 |

By group:

| Group | Features | Exact | Inspired | Ours |
|---|---|---|---|---|
| A. Base numbers | 8 | 8 | 0 | 0 |
| B. Ratios and scores | 46 | 23 | 21 | 2 |
| C. Trends and history | 17 | 3 | 14 | 0 |
| D. Industry comparison | 7 | 0 | 7 | 0 |
| E. Filing facts | 5 | 1 | 3 | 1 |
| F. NT late-filing notices | 2 | 0 | 2 | 0 |
| G. Warning phrases | 45 | 8 | 37 | 0 |

## How this was checked

- Papers in `Capstone/literature/` (du Jardin 2009, Alanis et al. 2022, Zhang et al. 2026, Fejér-Király 2015, Wang 2024) were read directly; page and table numbers are from those PDFs.
- The other papers were confirmed on the publisher, RePEc/IDEAS, SSRN, arXiv or university pages (URLs in the reference list).
- **Caution:** Whittred & Zimmer (1984) was only seen in reference lists. Beaver (1966) full ratio table was not seen. Zhang et al. (2026) is a preprint (not peer-reviewed).
- **Could not confirm, do not cite yet:** the variable lists of Jones, Johnstone & Wilson (2017, JBFA), Jones (2017, RAST) and Barboza, Kimura & Altman (2017, ESWA).

## A. Base numbers

| Feature | Type | Status | Source | How it is used |
|---|---|---|---|---|
| `total_assets` | Dollar | Exact | DJ09 | raw financial variables used unstandardized as predictors (p.5); inputs of every classic ratio |
| `current_assets` | Dollar | Exact | DJ09 | raw financial variables used unstandardized as predictors (p.5); inputs of every classic ratio |
| `current_liabilities` | Dollar | Exact | DJ09 | raw financial variables used unstandardized as predictors (p.5); inputs of every classic ratio |
| `total_liabilities` | Dollar | Exact | DJ09 | raw financial variables used unstandardized as predictors (p.5); inputs of every classic ratio |
| `revenue` | Dollar | Exact | DJ09 | raw financial variables used unstandardized as predictors (p.5); inputs of every classic ratio |
| `net_income` | Dollar | Exact | DJ09 | raw financial variables used unstandardized as predictors (p.5); inputs of every classic ratio |
| `operating_income` | Dollar | Exact | DJ09 | raw financial variables used unstandardized as predictors (p.5); inputs of every classic ratio |
| `operating_cash_flow` | Dollar | Exact | DJ09 | raw financial variables used unstandardized as predictors (p.5); inputs of every classic ratio |

## B. Ratios and scores

| Feature | Type | Status | Source | How it is used |
|---|---|---|---|---|
| `cash_to_current_liabilities` | Ratio | Inspired | DJ09 | liquidity ratio family (p.4); Beaver 1966 liquid-asset ratios |
| `months_of_cash` | Ratio | Inspired | ZH26 | "cash burn; burn rate" (Table 14) turned into a number |
| `retained_earnings_to_assets` | Ratio | Exact | A68 | Altman X2 (also AL22 p.5) |
| `equity_to_assets` | Ratio | Inspired | A00 | ZETA X6 capitalization; Ohlson OENEG |
| `interest_coverage` | Ratio | Exact | A00 | ZETA X3: EBIT / total interest payments |
| `working_capital_to_assets` | Ratio | Exact | A68 | Altman X1 (also AL22 p.5) |
| `ebit_to_assets` | Ratio | Exact | A68 | Altman X3 (also AL22 p.5) |
| `sales_to_assets` | Ratio | Exact | A68 | Altman X5 (also AL22 p.5) |
| `equity_to_liabilities` | Ratio | Exact | A00 | Z'' X4: book equity / total liabilities |
| `log_assets` | Ratio | Exact | O80 | SIZE; ZH26 Table 2 size |
| `liabilities_to_assets` | Ratio | Exact | O80 | TLTA; Zmijewski 1984; AL22 p.5 |
| `current_liabilities_to_current_assets` | Ratio | Exact | O80 | CLCA |
| `liabilities_exceed_assets` | Binary (0/1) | Exact | O80 | OENEG |
| `net_income_to_assets` | Ratio | Exact | O80 | NITA; Zmijewski; Shumway; ZH26 Table 2 |
| `cash_flow_to_liabilities` | Ratio | Exact | O80 | FUTL (funds from operations / TL) |
| `current_ratio` | Ratio | Exact | Z84 | CACL; ZH26 Table 2 liquidity |
| `cash_to_assets` | Ratio | Inspired | CHS08 | CASHMTA uses market assets; ours uses book |
| `quick_ratio` | Ratio | Exact | DJ09 | "current and quick ratios" (p.4) |
| `debt_due_to_cash` | Ratio | Inspired | ZH26 | "debt maturities; notes due" (Table 15) |
| `debt_to_assets` | Ratio | Exact | ZH26 | Table 2 leverage = total debt / total assets |
| `lease_liabilities_to_assets` | Ratio | Inspired | A00 | ZETA counts capitalized leases as debt |
| `interest_paid_to_cash_flow` | Ratio | Inspired | A00 | ZETA X3 debt service, cash version |
| `ebitda_to_liabilities` | Ratio | Inspired | B66 | Beaver's cash flow (NI + depreciation) / total debt |
| `payables_to_assets` | Ratio | Exact | DJ09 | "accounts payable/total assets" (p.4) |
| `gross_margin` | Ratio | Exact | AL22 | Gross Profit/Sales (Table 1) |
| `operating_margin` | Ratio | Exact | DJ09 | "net operating margin" (p.4) |
| `net_margin` | Ratio | Exact | DJ09 | "sales margin" (p.4) |
| `cash_flow_to_assets` | Ratio | Exact | ZH26 | Table 2 cash flow = OCF / total assets |
| `sga_to_revenue` | Ratio | Inspired | DJ09 | "production costs" indicator family (§3, Bardos 1995) |
| `rnd_to_assets` | Ratio | Inspired | BCM12 | R&D intensity changes how ratios predict bankruptcy |
| `stock_comp_to_assets` | Ratio | Ours (no paper found) | — | no paper found |
| `goodwill_to_assets` | Ratio | Inspired | ZH26 | "goodwill impairment" (Table 16) |
| `tangible_equity_to_assets` | Ratio | Inspired | ZH26 | equity without goodwill; Table 16 impairment |
| `receivables_to_revenue` | Ratio | Inspired | DJ09 | activity / turnover ratios (p.4) |
| `capex_to_assets` | Ratio | Ours (no paper found) | — | no paper found |
| `has_revenue` | Binary (0/1) | Inspired | A68 | sales/assets; ZH26 "decline in sales" (Table 16) |
| `financing_cash_flow_to_assets` | Ratio | Inspired | WW19 | distressed firms raise outside money |
| `investing_cash_flow_to_assets` | Ratio | Inspired | ZH26 | "asset sale to raise liquidity" (Table 17) |
| `stock_issued_to_assets` | Ratio | Inspired | WW19 | ~40% of equity issues come from distressed firms |
| `debt_issued_to_assets` | Ratio | Inspired | ZH26 | refinancing stress (Table 15) |
| `debt_repaid_to_assets` | Ratio | Inspired | ZH26 | "repaid debt; deleveraging" (Table 15) |
| `pays_dividends` | Binary (0/1) | Inspired | DD90 | distressed firms cut dividends; DJ09 p.2 |
| `debt_extinguishment_to_assets` | Ratio | Inspired | ZH26 | "debt restructuring; distressed exchange" (Table 15) |
| `altman_z2_risk` | Score | Exact | A00 | Z'' = 6.56X1+3.26X2+6.72X3+1.05X4 |
| `ohlson_o_score` | Score | Exact | O80 | O-score formula (also ZH26 App. A) |
| `zmijewski_score` | Score | Exact | Z84 | Zmijewski formula (also ZH26 App. A) |

## C. Trends and history

| Feature | Type | Status | Source | How it is used |
|---|---|---|---|---|
| `revenue_growth` | Ratio | Inspired | DJ09 | "variation variables": year-on-year changes (p.5); DJ15 |
| `asset_growth` | Ratio | Inspired | DJ09 | "variation variables": year-on-year changes (p.5); DJ15 |
| `cash_change_to_assets` | Ratio | Inspired | DJ09 | "variation variables": year-on-year changes (p.5); DJ15 |
| `equity_change_to_assets` | Ratio | Inspired | DJ09 | "variation variables": year-on-year changes (p.5); DJ15 |
| `liabilities_to_assets_change` | Ratio | Inspired | DJ09 | "variation variables": year-on-year changes (p.5); DJ15 |
| `net_income_to_assets_change` | Ratio | Inspired | DJ09 | "variation variables": year-on-year changes (p.5); DJ15 |
| `share_growth` | Ratio | Inspired | WW19 | share issuance by distressed firms (closest found) |
| `loss_two_years` | Binary (0/1) | Exact | O80 | INTWO |
| `net_income_change` | Ratio | Exact | O80 | CHIN, same formula |
| `cash_to_assets_change_since_last` | Ratio | Inspired | DJ15 | failure as a process over time; DJ09 p.5 |
| `net_income_to_assets_change_since_last` | Ratio | Inspired | DJ15 | failure as a process over time; DJ09 p.5 |
| `liabilities_to_assets_change_since_last` | Ratio | Inspired | DJ15 | failure as a process over time; DJ09 p.5 |
| `cash_flow_to_assets_change_since_last` | Ratio | Inspired | DJ15 | failure as a process over time; DJ09 p.5 |
| `losses_in_last_4` | Count | Inspired | O80 | INTWO extended to 4 reports |
| `reports_so_far` | Count | Inspired | SH01 | firm age (years listed), counted in reports |
| `years_since_first_report` | Days / years | Exact | SH01 | ln(age), years since listing |
| `days_since_last_report` | Days / years | Inspired | BK17 | late or missing filings signal poor performance |

## D. Industry comparison

| Feature | Type | Status | Source | How it is used |
|---|---|---|---|---|
| `net_income_to_assets_industry_percentile` | Percentile | Inspired | PP91 | industry-relative ratios (ratio / industry average); ours is a percentile rank. AL22 industry-year medians |
| `liabilities_to_assets_industry_percentile` | Percentile | Inspired | PP91 | industry-relative ratios (ratio / industry average); ours is a percentile rank. AL22 industry-year medians |
| `cash_to_assets_industry_percentile` | Percentile | Inspired | PP91 | industry-relative ratios (ratio / industry average); ours is a percentile rank. AL22 industry-year medians |
| `cash_flow_to_assets_industry_percentile` | Percentile | Inspired | PP91 | industry-relative ratios (ratio / industry average); ours is a percentile rank. AL22 industry-year medians |
| `equity_to_assets_industry_percentile` | Percentile | Inspired | PP91 | industry-relative ratios (ratio / industry average); ours is a percentile rank. AL22 industry-year medians |
| `log_assets_industry_percentile` | Percentile | Inspired | PP91 | industry-relative ratios (ratio / industry average); ours is a percentile rank. AL22 industry-year medians |
| `revenue_growth_industry_percentile` | Percentile | Inspired | PP91 | industry-relative ratios (ratio / industry average); ours is a percentile rank. AL22 industry-year medians |

## E. Filing facts

| Feature | Type | Status | Source | How it is used |
|---|---|---|---|---|
| `filer_status` | Category | Inspired | O80 | size class (Ohlson SIZE); no paper uses the SEC filer category |
| `filing_delay_days` | Days / years | Inspired | WZ84 | distressed firms report later; Alford et al. 1994 |
| `late_filer` | Binary (0/1) | Inspired | BK17 | filing after the deadline; Alford et al. 1994 |
| `is_10k` | Binary (0/1) | Ours (no paper found) | — | control for annual vs quarterly report |
| `industry` | Category | Exact | CJ04 | industry effects in the hazard model; AL22 industry dummies |

## F. NT late-filing notices

| Feature | Type | Status | Source | How it is used |
|---|---|---|---|---|
| `late_filing_notice_last_year` | Count | Inspired | BK17 | NT 10-K/10-Q "signal continued poor performance" |
| `days_since_late_filing_notice` | Days / years | Inspired | BK17 | same; Alford et al. 1994 (Form 12b-25) |

## G. Warning phrases

| Feature | Type | Status | Source | How it is used |
|---|---|---|---|---|
| `going_concern_in_report` | Binary (0/1) | Exact | ZH26 | "substantial doubt", "going concern" (Table 14); MSV15 |
| `going_concern_before_last_year` | Count | Inspired | MSV15 | same language in earlier filings (signal up to 3 years ahead) |
| `days_since_going_concern_before` | Days / years | Inspired | MSV15 | time since earlier filings had it |
| `forbearance_in_report` | Binary (0/1) | Exact | ZH26 | "forbearance agreement" (Table 15) |
| `forbearance_before_last_year` | Count | Inspired | MSV15 | same language in earlier filings (signal up to 3 years ahead) |
| `days_since_forbearance_before` | Days / years | Inspired | MSV15 | time since earlier filings had it |
| `minimum_bid_price_in_report` | Binary (0/1) | Inspired | RW12 | Nasdaq $1 bid-price rule; CHS08 low price |
| `minimum_bid_price_before_last_year` | Count | Inspired | MSV15 | same language in earlier filings (signal up to 3 years ahead) |
| `days_since_minimum_bid_price_before` | Days / years | Inspired | MSV15 | time since earlier filings had it |
| `chapter_11_in_report` | Binary (0/1) | Inspired | MAI19 | 10-K text features; ZH26 leaves Chapter 11 out |
| `chapter_11_before_last_year` | Count | Inspired | MSV15 | same language in earlier filings (signal up to 3 years ahead) |
| `days_since_chapter_11_before` | Days / years | Inspired | MSV15 | time since earlier filings had it |
| `strategic_alternatives_in_report` | Binary (0/1) | Exact | ZH26 | "strategic alternatives" (Table 17) |
| `strategic_alternatives_before_last_year` | Count | Inspired | MSV15 | same language in earlier filings (signal up to 3 years ahead) |
| `days_since_strategic_alternatives_before` | Days / years | Inspired | MSV15 | time since earlier filings had it |
| `material_weakness_in_report` | Binary (0/1) | Exact | ZH26 | "material weakness in internal control" (Table 17) |
| `material_weakness_before_last_year` | Count | Inspired | MSV15 | same language in earlier filings (signal up to 3 years ahead) |
| `days_since_material_weakness_before` | Days / years | Inspired | MSV15 | time since earlier filings had it |
| `identified_material_weakness_in_report` | Binary (0/1) | Exact | ZH26 | same phrase, stricter match (Table 17) |
| `identified_material_weakness_before_last_year` | Count | Inspired | MSV15 | same language in earlier filings (signal up to 3 years ahead) |
| `days_since_identified_material_weakness_before` | Days / years | Inspired | MSV15 | time since earlier filings had it |
| `not_in_compliance_in_report` | Binary (0/1) | Inspired | NSS12 | covenant violations found in SEC filings |
| `not_in_compliance_before_last_year` | Count | Inspired | MSV15 | same language in earlier filings (signal up to 3 years ahead) |
| `days_since_not_in_compliance_before` | Days / years | Inspired | MSV15 | time since earlier filings had it |
| `covenant_not_in_compliance_in_report` | Binary (0/1) | Exact | ZH26 | "breach / violation of covenant" (Table 15); NSS12 |
| `covenant_not_in_compliance_before_last_year` | Count | Inspired | MSV15 | same language in earlier filings (signal up to 3 years ahead) |
| `days_since_covenant_not_in_compliance_before` | Days / years | Inspired | MSV15 | time since earlier filings had it |
| `reverse_stock_split_in_report` | Binary (0/1) | Inspired | NT16 | ~80% of failed reverse-split firms delisted |
| `reverse_stock_split_before_last_year` | Count | Inspired | MSV15 | same language in earlier filings (signal up to 3 years ahead) |
| `days_since_reverse_stock_split_before` | Days / years | Inspired | MSV15 | time since earlier filings had it |
| `restructuring_support_agreement_in_report` | Binary (0/1) | Inspired | ZH26 | "debt restructuring" (Tables 15, 17) |
| `restructuring_support_agreement_before_last_year` | Count | Inspired | MSV15 | same language in earlier filings (signal up to 3 years ahead) |
| `days_since_restructuring_support_agreement_before` | Days / years | Inspired | MSV15 | time since earlier filings had it |
| `notice_of_default_in_report` | Binary (0/1) | Exact | ZH26 | "notice of default" (Table 15) |
| `notice_of_default_before_last_year` | Count | Inspired | MSV15 | same language in earlier filings (signal up to 3 years ahead) |
| `days_since_notice_of_default_before` | Days / years | Inspired | MSV15 | time since earlier filings had it |
| `debtor_in_possession_in_report` | Binary (0/1) | Inspired | EL23 | DIP loans to Chapter 11 firms |
| `debtor_in_possession_before_last_year` | Count | Inspired | MSV15 | same language in earlier filings (signal up to 3 years ahead) |
| `days_since_debtor_in_possession_before` | Days / years | Inspired | MSV15 | time since earlier filings had it |
| `cease_operations_in_report` | Binary (0/1) | Exact | ZH26 | "ceased operations" (Table 16) |
| `cease_operations_before_last_year` | Count | Inspired | MSV15 | same language in earlier filings (signal up to 3 years ahead) |
| `days_since_cease_operations_before` | Days / years | Inspired | MSV15 | time since earlier filings had it |
| `wind_down_in_report` | Binary (0/1) | Inspired | ZH26 | "going out of business" (Table 16) |
| `wind_down_before_last_year` | Count | Inspired | MSV15 | same language in earlier filings (signal up to 3 years ahead) |
| `days_since_wind_down_before` | Days / years | Inspired | MSV15 | time since earlier filings had it |

## References

| Key | Reference | What we used / where |
|---|---|---|
| A68 | Altman, E.I. (1968). Financial ratios, discriminant analysis and the prediction of corporate bankruptcy. Journal of Finance 23(4), 589–609. | Classic; X1–X5 definitions |
| A00 | Altman, E.I. (2000). Predicting financial distress of companies: Revisiting the Z-score and ZETA models. NYU Stern working paper. | Read: Z'' = 6.56X1+3.26X2+6.72X3+1.05X4 with book equity; ZETA X3 debt service = EBIT/interest (incl. capitalized leases), X6 capitalization. https://moodle2.units.it/pluginfile.php/322514/mod_resource/content/0/Zscores.pdf |
| O80 | Ohlson, J.A. (1980). Financial ratios and the probabilistic prediction of bankruptcy. Journal of Accounting Research 18(1), 109–131. | SIZE, TLTA, WCTA, CLCA, OENEG, NITA, FUTL, INTWO, CHIN. https://econpapers.repec.org/RePEc:bla:joares:v:18:y:1980:i:1:p:109-131 |
| Z84 | Zmijewski, M.E. (1984). Methodological issues related to the estimation of financial distress prediction models. Journal of Accounting Research 22 (supplement), 59–82. | NITA, TLTA, CACL |
| B66 | Beaver, W.H. (1966). Financial ratios as predictors of failure. Journal of Accounting Research 4 (supplement), 71–111. | Cash flow (NI + depreciation) / total debt. Full 30-ratio table NOT checked |
| SH01 | Shumway, T. (2001). Forecasting bankruptcy more accurately: A simple hazard model. Journal of Business 74(1), 101–124. | ln(age) = years since listing (not significant there). https://tylergshumway.org/Shumway-ForecastingBankruptcyAccurately-2001.pdf |
| CHS08 | Campbell, J.Y., Hilscher, J. & Szilagyi, J. (2008). In search of distress risk. Journal of Finance 63(6), 2899–2939. | CASHMTA (cash / market assets); low price per share. https://www.nber.org/papers/w12362 |
| CJ04 | Chava, S. & Jarrow, R.A. (2004). Bankruptcy prediction with industry effects. Review of Finance 8(4), 537–569. | Industry groupings in the hazard model. https://ideas.repec.org/a/oup/revfin/v8y2004i4p537-569..html |
| PP91 | Platt, H.D. & Platt, M.B. (1991). A note on the use of industry-relative ratios in bankruptcy prediction. Journal of Banking & Finance 15(6), 1183–1194. | Firm ratio / industry ratio. https://ideas.repec.org/a/eee/jbfina/v15y1991i6p1183-1194.html |
| DJ09 | du Jardin, P. (2009). Bankruptcy prediction models: How to choose the most relevant variables? Review of 190 studies. | In literature/. Table 1 p.4 (variable types); p.4 names current and quick ratios, sales margin, net operating margin, asset turnover, total debt/total assets, accounts payable/total assets; p.5 'variation variables' (year-on-year changes) and raw 'financial variables'; sec. 3 'production costs' (Bardos 1995) |
| DJ15 | du Jardin, P. (2015). Bankruptcy prediction using terminal failure processes. European Journal of Operational Research 242(1), 286–303. | Failure as a trajectory over time. https://ideas.repec.org/a/eee/ejores/v242y2015i1p286-303.html |
| AL22 | Alanis, E., Chava, S. & Shah, A. (2022). Benchmarking machine learning models to predict corporate bankruptcy. arXiv:2212.12051. | In literature/. p.5: ni/at, tl/at, nwc/at, re/at, ebit/at, sale/at; industry-year median tl/at; Fama-French industry dummies; Table 1: Gross Profit/Sales |
| ZH26 | Zhang, Z., Zheng, M., Zhang, T., Lin, L., Wang, Y. & Lin, L. (2026). Bankruptcy prediction from 10-K narratives: Evidence from interpretable text scores and accounting baselines. arXiv:2606.05623. PREPRINT. | In literature/. Table 2 p.10: log assets, total debt/assets, current ratio, NI/assets, OCF/assets. Phrase dictionary Appendix B: Table 14 p.31 (substantial doubt, going concern, cash burn), Table 15 p.32 (notice of default, forbearance agreement, breach/violation of covenant, debt maturities, debt restructuring, distressed exchange, repaid debt), Table 16 p.32 (ceased operations, going out of business, goodwill impairment, decline in sales), Table 17 p.33 (material weakness in internal control, strategic alternatives, asset sale to raise liquidity). Excludes Chapter 11 terms |
| MSV15 | Mayew, W.J., Sethuraman, M. & Venkatachalam, M. (2015). MD&A disclosure and the firm's ability to continue as a going concern. The Accounting Review 90(4), 1621–1651. | Going-concern language predicts bankruptcy up to 3 years ahead. https://scholars.duke.edu/publication/1096688 |
| MAI19 | Mai, F., Tian, S., Lee, C. & Ma, L. (2019). Deep learning models for bankruptcy prediction using textual disclosures. European Journal of Operational Research 274(2), 743–758. | 10-K text adds to ratios. https://ideas.repec.org/a/eee/ejores/v274y2019i2p743-758.html |
| NSS12 | Nini, G., Smith, D.C. & Sufi, A. (2012). Creditor control rights, corporate governance, and firm value. Review of Financial Studies 25(6), 1713–1761. | Covenant violations collected from SEC filings. https://ideas.repec.org/a/oup/rfinst/v25y2012i6p1713-1761.html |
| RW12 | Rhee, S.G. & Wu, F. (2012). Anything wrong with breaking a buck? An empirical evaluation of NASDAQ's $1 minimum bid price maintenance criterion. Journal of Financial Markets 15(2), 258–285. | https://ideas.repec.org/a/eee/finmar/v15y2012i2p258-285.html |
| NT16 | Neuhauser, K.L. & Thompson, T.H. (2016). Survivability following reverse stock splits: What determines the fate of non-surviving firms? Journal of Economics and Business 83, 1–22. | https://ideas.repec.org/a/eee/jebusi/v83y2016icp1-22.html |
| EL23 | Eckbo, B.E., Li, K. & Wang, W. (2023). Loans to Chapter 11 firms: Contract design, repayment risk, and pricing. Journal of Law and Economics 66(3), 465–509. | https://ideas.repec.org/a/ucp/jlawec/doi10.1086-724421.html |
| BK17 | Bartov, E. & Konchitchki, Y. (2017). SEC filings, regulatory deadlines, and capital market consequences. Accounting Horizons 31(4), 109–131. | NT 10-K/10-Q filings signal continued poor performance (full PDF read by the research agent) |
| WZ84 | Whittred, G. & Zimmer, I. (1984). Timeliness of financial reporting and financial distress. The Accounting Review 59(2), 287–295. | CAUTION: only seen in reference lists, paper not opened |
| DD90 | DeAngelo, H. & DeAngelo, L. (1990). Dividend policy and financial distress: An empirical investigation of troubled NYSE firms. Journal of Finance 45(5), 1415–1431. | https://ideas.repec.org/a/bla/jfinan/v45y1990i5p1415-31.html |
| WW19 | Walker, M.D. & Wu, Q. (2019). Equity issues when in distress. European Financial Management 25(3), 489–519. | https://econpapers.repec.org/RePEc:bla:eufman:v:25:y:2019:i:3:p:489-519 |
| BCM12 | Beaver, W.H., Correia, M. & McNichols, M.F. (2012). Do differences in financial reporting attributes impair the predictive ability of financial ratios for bankruptcy? Review of Accounting Studies 17(4), 969–1010. | R&D intensity used to split the sample, not as a predictor |

## Files

- `feature_sources.csv`: the same table, one row per feature (for filtering in Excel or pandas).
- `feature_sources_map.py`: the script that holds the mapping and checks it covers all 130 features.
