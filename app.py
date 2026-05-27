from flask import Flask, jsonify, render_template, request
from mma import get_fighters_stats, get_fighter_details

app = Flask(__name__)

fighters_cache = None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/fighter')
def fighter():
    return render_template('fighter.html')

@app.route('/api/fighters', methods=['GET'])
def get_fighters():
    global fighters_cache
    if fighters_cache is None:
        fighters_cache = get_fighters_stats()
    return jsonify(fighters_cache)

@app.route('/api/fighter', methods=['GET'])
def get_fighter():
    url = request.args.get('url')
    try:
        stats = get_fighter_details(url)
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
if __name__ == '__main__':
    app.run(debug=True)