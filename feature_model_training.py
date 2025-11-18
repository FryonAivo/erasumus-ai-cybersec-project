import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix

df = pd.read_csv('./datasets/phishing_url_features_combined_1.csv')

# This is just to check that the dataframe has loaded correctly
# print("Shape: ", df.shape)
# print("\nColumn names: ")
# print(df.columns.tolist())
# print("\nFirst columns: ")
# print(df.head())

target_column = 'phishing'
X = df.drop(target_column, axis=1)
y = df[target_column]

# Quick check if our dataset is balanced
# print("Class distribution: ")
# print(y.value_counts())

model = RandomForestClassifier(
    n_estimators=50,
    max_depth=15,
    min_samples_split=10,
    min_samples_leaf=5,
    random_state=1,
    n_jobs=1
)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=1
)

model.fit(X_train, y_train)

y_pred = model.predict(X_test)

print(classification_report(y_test, y_pred))
print(confusion_matrix(y_test, y_pred))