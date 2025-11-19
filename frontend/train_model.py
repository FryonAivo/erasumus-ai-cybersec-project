import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
import joblib 

#1. Dataset Creation
data = {
    'text': [
        #SAFE EXAMPLES (Label 0)
        'http://google.com', 
        'https://www.amazon.com',
        'Hi, here is the monthly report you asked for.',
        'The meeting is scheduled for tomorrow at 10:00 AM.', #::
        'Please find the attached invoice (PDF) for your purchase.', #()
        'Let us have lunch together?', #??
        'https://github.com/project-v1',
        'Welcome to our newsletter subscription.',
        'Project update: The deadline has been extended!',
        
        #PHISHING EXAMPLES (Label 1) 
        'http://banca-sicura-login.xyz', 
        'http://free-iphone-winner.net/login',
        'URGENT!!! Your account is locked. Click here to verify.', #!!
        '$$$ You have won a lottery! Claim your prize now $$$', #$$
        'Update your bank details immediately @ http://fake-site.com', #@
        'http://malicious-site.com/login?user=admin', #??==
        'Click this link to reset your password immediately: http://bit.ly/fake',
        'CONGRATULATIONS!!! You are the 100th visitor.',
        'Verify your identity #12345 to avoid suspension.' ###
    ],
    'label': [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1] 
}

print("Loading data...")
df = pd.DataFrame(data)

#2. Data Splitting
X = df['text']
y = df['label']

#Split data into training and testing sets (70% train, 30% test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

#3. Pipeline Construction
#TfidfVectorizer converts text to numerical vectors.
#LogisticRegression classifies the vectors.
model = make_pipeline(
    TfidfVectorizer(), 
    LogisticRegression()
)

#4. Model Training
print("Training the model...")
model.fit(X_train, y_train)

#5. Evaluation
y_pred = model.predict(X_test)
print("Model Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))

#6. Save the Model
#This file will be loaded by the web application.
joblib.dump(model, 'phishing_model.pkl')
print("Success! Model saved as 'phishing_model.pkl'")