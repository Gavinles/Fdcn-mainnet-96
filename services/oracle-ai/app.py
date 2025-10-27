from flask import Flask, request, jsonify
from flask_cors import CORS
import requests, os
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk

app = Flask(__name__)
CORS(app)

try: nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError: nltk.download('vader_lexicon', quiet=True)

STATE_LEDGER_URL = os.environ.get('STATE_LEDGER_URL', 'http://state-ledger:5002') 
sio = None # Placeholder for a potential real-time connection to the ledger

def get_co_pilot_guidance(text):
    analyzer = SentimentIntensityAnalyzer()
    sentiment = analyzer.polarity_scores(text)['compound']
    if sentiment > 0.5: return "The high-coherence, positive resonance of this insight is clear. Your contribution strengthens the network."
    if sentiment < -0.3: return "Acknowledging this difficult feeling is an act of courage. I am holding space for this experience."
    return "Insight anchored. The network reflects your awareness."

@app.route('/pocc/analyze', methods=['POST'])
def analyze_pocc():
    data = request.get_json()
    fex_reward = max(1.0, len(data.get('text', '')) / 15.0)
    su_reward = max(1, int(len(data.get('text', '')) / 30.0))
    try:
        requests.post(f"{STATE_LEDGER_URL}/transaction", json={'type': 'PoccReward', 'accountId': data.get('accountId'), 'fex_reward': fex_reward, 'su_reward': su_reward})
    except: return jsonify({'error': 'Ledger unavailable'}), 500
    guidance = get_co_pilot_guidance(data.get('text', ''))
    return jsonify({'status': 'success', 'guidance': guidance})

if __name__ == '__main__':
    print(">>> Oracle AI Service: ONLINE <<<")
    app.run(host='0.0.0.0', port=5001)
