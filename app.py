import streamlit as st
import joblib
import pandas as pd
from url_feature_extraction import extract_features  # Make sure this file contains your function


# -----------------------------
# MODEL LOADING
# -----------------------------
def load_model():
    try:
        return joblib.load('model.pkl')
    except:
        return None


# -----------------------------
# SIMPLE DB CHECKS
# -----------------------------
def check_databases(url):
    """
    Checks the whitelist and blacklist.
    Returns: (Status, Description, Probability) or None.
    """
    BLACKLIST = [
        "http://malicious-site.com",
        "http://virus-download.net",
        "bad-email@hacker.com"
    ]

    if url in BLACKLIST:
        return ("DANGER", "Found in known malicious Blacklist.", 1.0)

    WHITELIST = [
        "http://google.com",
        "https://google.com",
        "https://www.google.com",
        "https://www.amazon.com",
        "https://github.com"
    ]

    if url in WHITELIST:
        return ("SAFE", "Found in Trusted Whitelist.", 0.0)

    return None  # Continue to ML model


# -----------------------------
# MAIN PREDICTION LOGIC
# -----------------------------
def analyze_url(url, model):
    # 1. DB Check
    db_result = check_databases(url)
    if db_result:
        return db_result

    # 2. ML Model Check
    features = extract_features(url)
    df = pd.DataFrame([features])

    prediction = model.predict(df)[0]
    probability = model.predict_proba(df)[0][1]

    if prediction == 1:
        return ("PHISHING DETECTED", "Suspicious patterns found.", probability)
    else:
        return ("SAFE", "No threatening characteristics detected.", probability)


# -----------------------------
# STREAMLIT UI
# -----------------------------
st.set_page_config(page_title="Phishing Detector", page_icon="🛡️")
st.title("🛡️ AI Phishing Detection System")
st.markdown("### Erasmus AI & CyberSec Project")
st.markdown("Enter a URL to verify its safety.")

model = load_model()

if model is None:
    st.error("⚠️ ERROR: 'model.pkl' missing. Train the model before using the app.")
else:
    url_input = st.text_input("Paste URL:", placeholder="https://example.com")

    if st.button("Analyze URL"):
        if not url_input:
            st.warning("Please enter a URL.")
        else:
            with st.spinner("Analyzing URL with AI model..."):
                label, desc, probability = analyze_url(url_input, model)

            st.divider()
            col1, col2 = st.columns([2, 1])

            with col1:
                if label == "SAFE":
                    st.success(f"✅ STATUS: {label}")
                    st.balloons()
                elif label == "DANGER":
                    st.error(f"🚨 STATUS: {label}")
                else:
                    st.warning(f"⚠️ STATUS: {label}")

                st.write(f"**Report:** {desc}")

            with col2:
                st.write("**Risk Level:**")
                risk_score = int(probability * 100)
                st.progress(risk_score)
                st.caption(f"{risk_score}% Risk")

            with st.expander("Technical Details"):
                st.json({
                    "URL": url_input,
                    "Prediction": label,
                    "Risk Score": risk_score,
                    "Check Type": "Database" if probability in [0.0, 1.0] else "AI Model"
                })
