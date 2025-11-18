import pandas as pd

df = pd.read_csv('./datasets/phishing_url_features_combined_1.csv')

# Column/feature visualization
# print("Columns: ")
# columns = df.columns.to_list()
# for column in columns:
#     print(f"{column}")

# The head is basically a broad "overview" of the dataset
print(df.head())