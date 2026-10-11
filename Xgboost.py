import pandas as pd
import numpy as np
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier
from sklearn.metrics import average_precision_score
import shap

train = pd.read_csv("/Users/pramukhvenkateshkoushik/Downloads/dataset_paper/financial_train.csv")
test = pd.read_csv("/Users/pramukhvenkateshkoushik/Downloads/dataset_paper/financial_test.csv")

feature_col = [column for column in train.columns if column not in {"cik", "fyear", "status_label"}]

y_train = train["status_label"].map({"alive": 0, "failed": 1})
y_test = test["status_label"].map({"alive": 0, "failed": 1})

model = XGBClassifier(
    objective="binary:logistic",
    n_estimators=300,
    learning_rate=0.04,
    subsample=0.8,
    colsample_bytree=0.8,
    eval_metric="aucpr",
    random_state=42,
    n_jobs=-1,
)
model.fit(train[feature_col], y_train)

row_number = 45
row = test[feature_col].iloc[row_number]
score = model.predict_proba(row.values.reshape(1, -1))[0][1]

print(f"Model score: {score:.3f}")
print(f"Test PR-AUC: {average_precision_score(y_test, model.predict_proba(test[feature_col])[:, 1]):.3f}")

explainer = shap.TreeExplainer(model, train[feature_col])
explainer_val = explainer(test[feature_col]).values

if explainer_val.ndim == 3:
    explainer_val = explainer_val[:,:,1]

case_shap = explainer_val[row_number]

ranked_factors = sorted(
    zip(feature_col, case_shap),
    key=lambda item: abs(item[1]),
    reverse=True,
)

for feature, contribution in ranked_factors[:10]:
    direction = "pushes score higher" if contribution > 0 else "pushes score lower"
    print(feature, round(float(contribution), 4), direction)



