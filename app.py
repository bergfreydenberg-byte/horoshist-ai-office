#!/usr/bin/env python3
"""
Horoshist AI Office — Backend proxy for YClients API
Runs on Render.com (free tier)
"""

import os, json, requests
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder='static')
CORS(app)

PARTNER_TOKEN = os.environ.get('YCLIENTS_TOKEN', 'l24oXa1Mg26Dw6VW63CE')
SALON_ID      = os.environ.get('SALON_ID', '124859')
YCLIENTS_BASE = 'https://api.yclients.com/api/v1'

def ycl_headers():
    return {
        'Authorization': f'Bearer {PARTNER_TOKEN}',
        'Accept': 'application/vnd.yclients.v2+json',
        'Content-Type': 'application/json',
    }

def ycl_get(path, params=None):
    url = f'{YCLIENTS_BASE}{path}'
    r = requests.get(url, headers=ycl_headers(), params=params, timeout=10)
    return r.json()

def ycl_post(path, data=None):
    url = f'{YCLIENTS_BASE}{path}'
    r = requests.post(url, headers=ycl_headers(), json=data or {}, timeout=10)
    return r.json()

# ── Serve frontend ──────────────────────────────────────────────
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

# ── API routes ──────────────────────────────────────────────────
@app.route('/api/bookings')
def bookings():
    date = request.args.get('date', '')
    params = {
        'start_date': date,
        'end_date': date,
        'count': 200,
        'page': 1,
    }
    data = ycl_get(f'/records/{SALON_ID}', params)
    return jsonify(data)

@app.route('/api/staff')
def staff():
    data = ycl_get(f'/company/{SALON_ID}/staff')
    return jsonify(data)

@app.route('/api/clients')
def clients():
    params = {
        'count': request.args.get('count', 30),
        'page':  request.args.get('page', 1),
    }
    data = ycl_get(f'/clients/{SALON_ID}', params)
    return jsonify(data)

@app.route('/api/analytics')
def analytics():
    date = request.args.get('date', '')
    params = {'start_date': date, 'end_date': date}
    data = ycl_get(f'/analytics/finance/{SALON_ID}', params)
    return jsonify(data)

@app.route('/api/reviews')
def reviews():
    params = {'count': 20, 'page': 1}
    data = ycl_get(f'/reviews/{SALON_ID}', params)
    return jsonify(data)

@app.route('/api/services')
def services():
    data = ycl_get(f'/company/{SALON_ID}/services')
    return jsonify(data)

@app.route('/api/salon')
def salon():
    data = ycl_get(f'/company/{SALON_ID}')
    return jsonify(data)

# Health check for Render
@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'salon': SALON_ID})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8888))
    print(f'\n🔥 Horoshist AI Office → http://localhost:{port}\n')
    app.run(host='0.0.0.0', port=port, debug=False)
