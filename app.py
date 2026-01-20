from flask import Flask, render_template, request
import pickle
import numpy as np
import re 
import csv
from urllib.parse import urlparse
from feature_extractor import FeatureExtractor

app = Flask(__name__)

# --- CONFIGURATION ---
MODEL_PATH = 'trainedmodel.pkl'
WHITELIST_FILE = 'top_sites.csv'

# 1. Load AI Model
try:
    model = pickle.load(open(MODEL_PATH, 'rb'))
except FileNotFoundError:
    print(f"ERROR: {MODEL_PATH} not found!")
    exit()

# 2. Load Whitelist Database (into a Hash Set for O(1) speed)
WHITELIST_SET = set()
try:
    with open(WHITELIST_FILE, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if row: # Skip empty lines
                domain = row[0].strip().lower()
                WHITELIST_SET.add(domain)
                # Auto-add 'www.' version too just in case
                WHITELIST_SET.add(f"www.{domain}")
    print(f"SUCCESS: Loaded {len(WHITELIST_SET)} domains into Whitelist.")
except FileNotFoundError:
    print(f"WARNING: {WHITELIST_FILE} not found. Whitelist feature disabled.")


def is_valid_url(url: str) -> bool:
    """
    Enhanced URL validation for the phishing detector.
    Returns True if the URL is valid, False otherwise.
    """
    if not url or len(url) > 2048:
        return False
    
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    
    try:
        parsed = urlparse(url)
        if not parsed.netloc:
            return False
            
        domain_parts = parsed.netloc.split('.')
        if len(domain_parts) < 2:
            return False
            
        domain_pattern = r'^[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9](\.[a-zA-Z]{2,})+$'
        if not re.match(domain_pattern, parsed.netloc):
            return False
            
        return True
    except:
        return False

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    url = request.form['url'].strip()
    
    # --- STEP 1: INPUT VALIDATION ---
    if not is_valid_url(url):
        return render_template('index.html', 
                             prediction_text="INVALID URL: Please enter a format like 'google.com'", 
                             url_input=url, prob=0, css_class="danger")

    # --- STEP 2: WHITELIST CHECK (The "Fast Lane") ---
    try:
        if not url.startswith(('http://', 'https://')):
             temp_url = 'http://' + url
        else:
             temp_url = url
        
        domain = urlparse(temp_url).netloc.lower()
        
        # Check if domain exists in our loaded set
        if domain in WHITELIST_SET:
             return render_template('index.html', 
                             prediction_text=f"WEBSITE IS SAFE (Verified Entity: {domain})", 
                             url_input=url,
                             prob=0.00,
                             css_class="safe")
    except:
        pass

    
    # --- STEP 3: FEATURE EXTRACTION  ---
    try:
        extractor = FeatureExtractor(url)
        features = extractor.extract_features()
    except Exception:
        return render_template('index.html',
                             prediction_text="ERROR: Could not process this URL structure",
                             url_input=url, prob=0, css_class="danger")
    
    # --- STEP 4: AI MODEL PREDICTION ---
    features_array = np.array(features).reshape(1, -1)
    
    try:
        probability = model.predict_proba(features_array)[0][1]
    except Exception:
        return render_template('index.html',
                             prediction_text="ERROR: Model prediction failed",
                             url_input=url, prob=0, css_class="danger")
    
    # --- STEP 5: HYBRID RISK RULES ---
    is_phishing = False
    risk_factors = []
    
    if probability > 0.5:
        is_phishing = True
        risk_factors.append("High AI Confidence")
    
    # Heuristics
    if len(url) > 60:
        probability += 0.1
        risk_factors.append("Suspicious Length")
    if url.count('-') >= 3:
        probability += 0.1
        risk_factors.append("Excessive Hyphens")
    if '@' in url:
        probability += 0.2
        risk_factors.append("Malicious Symbol '@'")
    if '?' in url and '=' in url.split('?')[-1]:
        probability += 0.1
        risk_factors.append("Suspicious Parameters")
    
    probability = min(0.99, probability)
    phishing_prob = round(probability * 100, 2)
    
    # --- STEP 6: FINAL VERDICT ---
    if is_phishing or probability > 0.5:
        reason_str = f"({', '.join(risk_factors)})" if risk_factors else ""
        text = f"PHISHING DETECTED! {reason_str}"
        color_class = "danger"
    else:
        text = "WEBSITE APPEARS SAFE"
        color_class = "safe"
        
    return render_template('index.html', 
                         prediction_text=text, 
                         url_input=url, 
                         prob=phishing_prob,
                         css_class=color_class)

if __name__ == '__main__':
    app.run(debug=True)