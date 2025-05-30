from flask import Flask, jsonify, request, render_template
from mma import get_fighters_stats, get_fighter_details

app = Flask(__name__)

fighters_list = get_fighters_stats()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/fighters', methods=['GET'])
def get_fighters():
    return jsonify(fighters_list)

if __name__ == '__main__':
    app.run(debug=True)
