from flask import Flask, jsonify, request, send_from_directory
import requests
import os

app = Flask(__name__, static_folder='.')

PRODUCTS_API = "http://reverseauction.com.mm/api/front/product/bid"
BID_HISTORY_API = "http://www.reverseauction.com.mm/api/front/bid/history"

HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent":
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    "Content-Type": "application/json",
    "Origin": "http://www.reverseauction.com.mm",
    "Referer": "http://www.reverseauction.com.mm/up-next",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-US,en;q=0.9,my;q=0.8",
    "Connection": "close"
}


@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)


@app.route('/api/products')
def get_products():
    try:
        response = requests.get(PRODUCTS_API, headers=HEADERS, timeout=30)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"success": False, "error": str(e), "data": []}), 500


@app.route('/api/bid-history')
def get_bid_history():
    cp_id = request.args.get('cp_id', '')
    page_size = request.args.get('pageSize', '100000')
    current = request.args.get('current', '1')
    sort = request.args.get('sort', 'desc')

    url = f"{BID_HISTORY_API}?pageSize={page_size}&current={current}&sort={sort}&cp_ids={cp_id}"

    try:
        response = requests.get(url, headers=HEADERS, timeout=60)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"success": False, "error": str(e), "data": []}), 500


@app.route('/api/image')
def proxy_image():
    image_url = request.args.get('url', '')
    if not image_url:
        return 'No URL provided', 400

    if not image_url.startswith('http://reverseauction.com.mm'):
        return 'Invalid image URL', 400

    try:
        response = requests.get(image_url,
                                headers={
                                    "User-Agent": HEADERS["User-Agent"],
                                    "Referer":
                                    "http://www.reverseauction.com.mm/"
                                },
                                timeout=30)
        response.raise_for_status()

        from flask import Response
        return Response(response.content,
                        mimetype=response.headers.get('Content-Type',
                                                      'image/png'))
    except requests.exceptions.RequestException as e:
        return str(e), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
