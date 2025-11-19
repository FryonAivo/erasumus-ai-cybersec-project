import streamlit as st
import joblib
import re 

#BACKEND SERVICES

def load_model():
    """Loads the pre-trained machine learning model."""
    try:
        return joblib.load('phishing_model.pkl')
    except:
        return None

def is_valid_format(text, input_type):
    """Validates the format of the input."""
    if input_type == "URL":
        regex = r"(http|https)://[a-zA-Z0-9./?=_-]+"
        return re.match(regex, text) is not None
    elif input_type == "Email Body":
        return len(text) > 5
    return True

def check_databases(text):
    """
    Checks both Blacklist AND Whitelist.
    Returns: (Status, Description, Probability) or None if not found.
    """
    # 1. BLACKLIST (Threats)
    BLACKLIST = [
        "http://malicious-site.com", 
        "http://virus-download.net",
        "bad-email@hacker.com"
    ]
    if text in BLACKLIST:
        return "DANGER", "Identified in the known malicious database (Blacklist).", 1.0
    
    # 2. WHITELIST (Safe Sites - The "Safety Net")
    WHITELIST = [
        "http://google.com",
        "https://google.com",
        "https://www.google.com",
        "https://www.amazon.com",
        "https://github.com"
    ]
    if text in WHITELIST:
        return "SAFE", "Identified in the Safe-Site Database (Whitelist).", 0.0
        
    return None # Not found in any DB, proceed to AI

def analyze_input(text, model):
    """Main logic."""
    
    # Step 1: Check Databases (Backend Service)
    db_result = check_databases(text)
    if db_result is not None:
        return db_result[0], db_result[1], db_result[2]
    
    # Step 2: ML Model Prediction (Only if not in DB)
    prediction = model.predict([text])[0] 
    probability = model.predict_proba([text])[0][1] 
    
    if prediction == 1:
        return "PHISHING DETECTED", f"The AI model detected suspicious patterns.", probability
    else:
        return "SAFE", f"The AI model analysis passed. No threats found.", probability

#FRONTEND UI (Streamlit)

st.set_page_config(page_title="Phishing Detector", page_icon="🛡️")
st.title("🛡️ AI Phishing Detection System")
st.markdown("### Erasmus AI & CyberSec Project")
st.markdown("Enter a URL or Email content to verify its safety.")

model = load_model()

if model is None:
    st.error("⚠️ ERROR: Model file 'phishing_model.pkl' not found. Please run 'train_model.py' first!")
else:
    st.sidebar.header("Input Type")
    option = st.sidebar.selectbox("Select Input:", ("URL", "Email Body"))

    user_input = ""
    if option == "URL":
        user_input = st.text_input("Paste URL:", placeholder="http://example.com")
    else:
        user_input = st.text_area("Paste Email:", height=150)

    if st.button("Analyze Input"):
        if not user_input:
            st.warning("Please enter text.")
        else:
            with st.spinner('Scanning databases and running AI model...'):
               
                result_label, result_desc, probability = analyze_input(user_input, model)
            
            st.divider()
            col1, col2 = st.columns([2, 1])
            
            with col1:
                if result_label == "SAFE":
                    st.success(f"✅ STATUS: {result_label}")
                    st.balloons()
                elif result_label == "DANGER":
                    st.error(f"🚨 STATUS: {result_label}")
                else:
                    st.warning(f"⚠️ STATUS: {result_label}")
                st.write(f"**Report:** {result_desc}")

            with col2:
                st.write("**Risk Level:**")
                risk_score = int(probability * 100)
                st.progress(risk_score)
                st.caption(f"{risk_score}% Risk")
                
            with st.expander("View Technical Details"):
                 st.json({
                    "Input": user_input,
                    "Prediction": result_label,
                    "Risk Score": risk_score,
                    "Check Type": "Database" if probability in [0.0, 1.0] else "AI Model"
                })