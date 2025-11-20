# feature_model_training.py
import pandas as pd
import joblib

from xgboost import XGBClassifier

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import OneHotEncoder, FunctionTransformer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.metrics import classification_report, confusion_matrix

from url_feature_extraction import extract_features
from transform_utils import select_url_column, select_numeric_columns


# ------------------------------------------------------------
# Load dataset
# ------------------------------------------------------------
df = pd.read_csv("./datasets/main_dataset.csv")

urls = df["URL"].tolist()
labels = df["label"].tolist()

numeric_rows = [extract_features(u) for u in urls]
X_num = pd.DataFrame(numeric_rows)
y = pd.Series(labels)

# Build training dataframe (URL + numeric features)
X_full = X_num.copy()
X_full.insert(0, "url", urls)


# ------------------------------------------------------------
# Define transformers
# ------------------------------------------------------------
tfidf_pipeline = Pipeline([
    ("select_url", FunctionTransformer(select_url_column, validate=False)),
    ("tfidf", TfidfVectorizer(
        analyzer="char_wb",
        ngram_range=(3, 5),
        min_df=5
    )),
])

cat_cols = ["TLD"]

numeric_pipeline = Pipeline([
    ("select_numeric", FunctionTransformer(select_numeric_columns, validate=False)),
    ("encode", ColumnTransformer(
        transformers=[
            ("tld", OneHotEncoder(handle_unknown="ignore"), cat_cols)
        ],
        remainder="passthrough",
    )),
])


# ------------------------------------------------------------
# Combine numeric + TF-IDF
# ------------------------------------------------------------
combined_features = FeatureUnion([
    ("tfidf", tfidf_pipeline),
    ("numeric", numeric_pipeline)
])


# ------------------------------------------------------------
# XGBoost model
# (parameters kept modest to match your previous RF behavior)
# ------------------------------------------------------------
model = XGBClassifier(
    n_estimators=350,
    max_depth=12,
    learning_rate=0.1,
    subsample=0.9,
    colsample_bytree=0.9,
    objective="binary:logistic",
    eval_metric="logloss",
    n_jobs=12,
    tree_method="hist"   # fastest + best for large sparse inputs
)


# ------------------------------------------------------------
# Full pipeline
# ------------------------------------------------------------
pipeline = Pipeline([
    ("features", combined_features),
    ("model", model),
])


# ------------------------------------------------------------
# Split, train, evaluate
# ------------------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X_full, y, test_size=0.2, stratify=y
)

pipeline.fit(X_train, y_train)

joblib.dump(pipeline, "model.pkl")

pred = pipeline.predict(X_test)
print(classification_report(y_test, pred))
print(confusion_matrix(y_test, pred))
