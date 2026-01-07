from flask import Flask, render_template, request
import pickle
import numpy as np
from feature_extractor import FeatureExtractor

app = Flask(__name__)

try:
    model = pickle.load(open('trainedmodel.pkl', 'rb'))
except FileNotFoundError:
    print("ERROR: trainedmodel.pkl not found!")
    exit()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    url = request.form['url']
    
    # 1. Run the Extractor
    extractor = FeatureExtractor(url)
    features = extractor.extract_features()
    
    # 2. Prepare for Model
    features_array = np.array(features).reshape(1, -1)
    
    # 3. Ask Model for Prediction
    probability = model.predict_proba(features_array)[0][1] 
    phishing_prob = round(probability * 100, 2)

    # If probability is greater than 50%, it IS Phishing.
    if probability > 0.5:
        text = "PHISHING DETECTED!"
        color_class = "danger"
    else:
        text = "WEBSITE IS SAFE"
        color_class = "safe"

    # 5. Return Template
    return render_template('index.html', 
                           prediction_text=text, 
                           url_input=url, 
                           prob=phishing_prob,
                           css_class=color_class)

if __name__ == '__main__':
    app.run(debug=True)