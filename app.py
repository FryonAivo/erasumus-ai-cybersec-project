# app.py
import streamlit as st
import joblib
import pandas as pd

from url_feature_extraction import extract_features
from transform_utils import select_url_column, select_numeric_columns



# ------------------------------------------------------------
# RULE ENGINE (Paranoia Mode)
# ------------------------------------------------------------
def rule_based_checks(url: str, feats: dict):
    # Suspicious TLD
    if feats["IsRiskyTLD"]:
        return True

    # High randomness (common in phishing kits)
    if feats["Entropy"] > 4.2:
        return True

    # Long URLs are highly suspicious
    if feats["URLLength"] > 120:
        return True

    # Too many subdomains (hidden phishing)
    if feats["SubdomainCount"] >= 3:
        return True

    # Unicode (IDN homograph)
    if feats["ContainsUnicode"]:
        return True

    # "@" inside URL
    if feats["HasAtSymbol"]:
        return True

    # Digit-heavy (randomized phishing paths)
    if feats["DigitRatio"] > 0.35:
        return True

    # Keyword-based flags
    phishing_keywords = [
        "login", "signin", "secure", "verify", "wallet",
        "reset", "update", "confirm", "checkout"
    ]
    if any(k in url.lower() for k in phishing_keywords):
        return True

    return False


# ------------------------------------------------------------
# ML + Rule Engine Decision
# ------------------------------------------------------------
def analyze_url(url: str, model):
    # Extract structured numeric features
    feats = extract_features(url)

    # RULE OVERRIDE (very suspicious → bypass ML)
    if rule_based_checks(url, feats):
        return (
            "PHISHING",
            "Rule-based suspicion triggered",
            0.99,
            feats
        )

    # Prepare data for model (must match training format)
    row = feats.copy()
    row["url"] = url

    X_df = pd.DataFrame([row])

    # ML prediction
    prob_phish = model.predict_proba(X_df)[0][1]
    label = "PHISHING" if prob_phish > 0.45 else "SAFE"

    return label, "ML-based decision", prob_phish, feats


# ------------------------------------------------------------
# STREAMLIT UI
# ------------------------------------------------------------
st.set_page_config(page_title="URL Phishing Detector", page_icon="🛡️")
st.title("🛡️ Hybrid Phishing Detector")
st.write("This system uses lexical analysis, numeric URL features, ML, and a paranoia rule engine.")

# Load Model
model = joblib.load("model.pkl")

# Input
url_input = st.text_input("Enter URL to analyze:", placeholder="https://example.com")

if st.button("Analyze URL"):
    if not url_input.strip():
        st.warning("Please enter a URL.")
    else:
        label, reason, probability, feats = analyze_url(url_input, model)

        st.subheader(f"Result: **{label}**")
        st.write(f"Reason: **{reason}**")
        st.write(f"Suspicion Score: **{probability:.2f}**")

        st.progress(float(probability))

        with st.expander("Show Extracted Feature Values"):
            st.json(feats)
