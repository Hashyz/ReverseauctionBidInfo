from flask import Flask, send_from_directory, jsonify, request
import requests

app = Flask(__name__, static_folder='.')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json',
    'Accept-Language': 'en-US,en;q=0.9'
}

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('.', path)

@app.route('/api/products')
def get_products():
    try:
        r = requests.get(
            'https://reverseauction.com.mm/gateway/campaignproduct/active',
            headers=HEADERS,
            timeout=15
        )
        return jsonify(r.json())
    except requests.exceptions.ConnectionError:
        return jsonify({'data': [], 'error': 'API server not responding'})
    except Exception as e:
        return jsonify({'data': [], 'error': str(e)})

@app.route('/api/bid-history')
def get_bid_history():
    try:
        cp_id = request.args.get('cp_id')
        url = f'https://reverseauction.com.mm/gateway/bid/bidhistory-web?cp_id={cp_id}&pageSize=100000&current=1&sort=desc'
        r = requests.get(url, headers=HEADERS, timeout=15)
        return jsonify(r.json())
    except requests.exceptions.ConnectionError:
        return jsonify({'data': [], 'error': 'API server not responding'})
    except Exception as e:
        return jsonify({'data': [], 'error': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
