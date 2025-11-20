import pandas as pd
import joblib

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, confusion_matrix

# Load dataset
df = pd.read_csv('./datasets/main_dataset.csv')

# Columns to drop due to high cardinality / noise
DROP_COLS = ["FILENAME", "URL", "Domain"]

# Drop them safely if present
df = df.drop(columns=[c for c in DROP_COLS if c in df.columns])

target_column = "label"

X = df.drop(target_column, axis=1)
y = df[target_column]

# Keep ONLY TLD as categorical
categorical_cols = ["TLD"] if "TLD" in X.columns else []

# Drop ALL other object columns
other_object_cols = X.select_dtypes(include=["object"]).columns
other_object_cols = [c for c in other_object_cols if c not in categorical_cols]

X = X.drop(columns=other_object_cols)

# Recompute numeric columns
numeric_cols = X.select_dtypes(exclude=["object"]).columns.tolist()

preprocess = ColumnTransformer(
    transformers=[
        ("tld", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_cols),
    ],
    remainder='passthrough'
)

model = RandomForestClassifier(
    n_estimators=150,
    max_depth=22,
    min_samples_split=8,
    min_samples_leaf=4,
    n_jobs=4
)

pipeline = Pipeline(steps=[
    ("preprocess", preprocess),
    ("model", model)
])

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y
)

pipeline.fit(X_train, y_train)

joblib.dump(pipeline, "model.pkl")

y_pred = pipeline.predict(X_test)

print(classification_report(y_test, y_pred))
print("Confusion matrix:\n")
print(confusion_matrix(y_test, y_pred))
