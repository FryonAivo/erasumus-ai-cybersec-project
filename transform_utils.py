import pandas as pd

def select_url_column(X):
    """Return URL column (Series of raw strings)."""
    return X["url"]

def select_numeric_columns(X):
    """Return numeric features (all except URL column)."""
    return X.drop(columns=["url"])
