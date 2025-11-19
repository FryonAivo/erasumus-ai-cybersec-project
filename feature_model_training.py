import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

df = pd.read_csv('./datasets/phishing_url_features_combined_1.csv')

target_column = 'phishing'
X = df.drop(target_column, axis=1)
y = df[target_column]

# The main ensemble model we're gonna use for decision-making
model = RandomForestClassifier(
    n_estimators=50,
    max_depth=15,
    min_samples_split=10,
    min_samples_leaf=5,
    random_state=1,
    n_jobs=1
)

# Example Decision Tree classifier for cross-testing
# model_2 = DecisionTreeClassifier(
#     max_depth=15,
#     min_samples_split=10,
#     min_samples_leaf=5,
#     random_state=1,
# )

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=1
)

model.fit(X_train, y_train)

# model_2.fit(X_train,y_train)

y_pred = model.predict(X_test)

# y_pred_2 = model_2.predict(X_test)

print(classification_report(y_test, y_pred))
print(f"Confusion matrix: \n")
print(confusion_matrix(y_test, y_pred))

# print("Model 2 result: \n")
# print(classification_report(y_test, y_pred_2))