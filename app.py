# app.py
import streamlit as st
import joblib
import pandas as pd

from url_feature_extraction import extract_features


# ------------------------------------------------------------
# RISK CATEGORY MAPPING (5 levels)
# ------------------------------------------------------------
def risk_category(prob):
    if prob < 0.15:
        return "Very Safe"
    elif prob < 0.35:
        return "Low Risk"
    elif prob < 0.60:
        return "Suspicious"
    elif prob < 0.85:
        return "High Risk"
    else:
        return "Critical (Likely Phishing)"


# ------------------------------------------------------------
# RULE ENGINE (Paranoia Mode)
# ------------------------------------------------------------
def rule_based_checks(url: str, feats: dict):
    if feats["IsRiskyTLD"]:
        return True

    if feats["Entropy"] > 4.2:
        return True

    if feats["URLLength"] > 120:
        return True

    if feats["SubdomainCount"] >= 3:
        return True

    if feats["ContainsUnicode"]:
        return True

    if feats["HasAtSymbol"]:
        return True

    if feats["DigitRatio"] > 0.35:
        return True

    phishing_keywords = [
        "login", "signin", "secure", "verify", "wallet",
        "reset", "update", "confirm", "checkout"
    ]
    if any(k in url.lower() for k in phishing_keywords):
        return True

    return False


# ------------------------------------------------------------
# ML + RULE ENGINE DECISION PIPELINE
# ------------------------------------------------------------
def analyze_url(url: str, model):
    feats = extract_features(url)

    # RULE OVERRIDE
    if rule_based_checks(url, feats):
        category = "Critical (Likely Phishing)"
        return (
            "PHISHING",
            "Rule-based suspicion triggered",
            0.99,
            category,
            feats
        )

    # ML PREDICTION
    row = feats.copy()
    row["url"] = url
    X_df = pd.DataFrame([row])

    prob = model.predict_proba(X_df)[0][1]
    label = "PHISHING" if prob > 0.45 else "SAFE"
    category = risk_category(prob)

    return label, "ML-based decision", prob, category, feats


# ------------------------------------------------------------
# STREAMLIT UI
# ------------------------------------------------------------
st.set_page_config(page_title="URL Phishing Detector", page_icon="🛡️")

st.title("🛡️ Hybrid Phishing Detector (URL-Only)")
st.write("Combines lexical ML features, numeric URL features, and a paranoid rule engine.")


# Load model
model = joblib.load("model.pkl")

# User input
url_input = st.text_input(
    "Enter a URL to analyze:",
    placeholder="https://example.com"
)

if st.button("Analyze URL"):
    if not url_input.strip():
        st.warning("Please enter a URL.")
    else:
        label, reason, probability, category, feats = analyze_url(url_input, model)

        st.subheader(f"Result: **{label}**")
        st.write(f"Risk Category: **{category}**")
        st.write(f"Reason: **{reason}**")
        st.write(f"Suspicion Score: **{probability:.2f}**")
        st.progress(float(probability))

        with st.expander("Show Extracted Features"):
            st.json(feats)
