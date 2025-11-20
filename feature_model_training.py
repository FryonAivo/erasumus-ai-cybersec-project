# model_training.py
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import OneHotEncoder, FunctionTransformer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.ensemble import RandomForestClassifier
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

# Full input DF for model
X_full = X_num.copy()
X_full.insert(0, "url", urls)


# ------------------------------------------------------------
# Transformers
# ------------------------------------------------------------
url_selector = FunctionTransformer(select_url_column, validate=False)
num_selector = FunctionTransformer(select_numeric_columns, validate=False)

tfidf_pipeline = Pipeline([
    ("select_url", url_selector),
    ("tfidf", TfidfVectorizer(
        analyzer="char_wb",
        ngram_range=(3, 5),
        min_df=2
    )),
])

cat_cols = ["TLD"]
numeric_pipeline = Pipeline([
    ("select_numeric", num_selector),
    ("encode", ColumnTransformer(
        transformers=[
            ("tld", OneHotEncoder(handle_unknown="ignore"), cat_cols)
        ],
        remainder="passthrough",
    )),
])


# ------------------------------------------------------------
# Combined feature space
# ------------------------------------------------------------
combined_features = FeatureUnion([
    ("tfidf", tfidf_pipeline),
    ("numeric", numeric_pipeline),
])


# ------------------------------------------------------------
# Model
# ------------------------------------------------------------
model = RandomForestClassifier(
    n_estimators=350,
    max_depth=40,
    min_samples_split=3,
    min_samples_leaf=2,
    class_weight="balanced",
    n_jobs=4
)

pipeline = Pipeline([
    ("features", combined_features),
    ("model", model),
])


# ------------------------------------------------------------
# Train-test split
# ------------------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X_full, y, test_size=0.2, stratify=y
)

# Fit model
pipeline.fit(X_train, y_train)

# SAVE — now works because no lambdas exist
joblib.dump(pipeline, "model.pkl")

# Evaluate
pred = pipeline.predict(X_test)
print(classification_report(y_test, pred))
print(confusion_matrix(y_test, pred))
