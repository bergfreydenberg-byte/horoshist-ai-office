#!/usr/bin/env python3
"""
Horoshist AI Office — YClients proxy with proper auth
"""
 
import os, requests
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
 
app = Flask(__name__, static_folder='static')
CORS(app)
 
PARTNER_TOKEN = os.environ.get('YCLIENTS_TOKEN', 'l24oXa1Mg26Dw6VW63CE')
SALON_ID      = os.environ.get('SALON_ID', '124859')
LOGIN         = os.environ.get('YCLIENTS_LOGIN', '')
PASSWORD      = os.environ.get('YCLIENTS_PASSWORD', '')
BASE          = 'https://api.yclients.com/api/v1'
 
_user_token = None
 
def get_user_token():
    global _user_token
    if _user_token:
        return _user_token
    try:
        r = requests.post(f'{BASE}/auth', json={
            'login': LOGIN,
            'password': PASSWORD,
            'type': 'user'
        }, headers={
            'Authorization': f'Bearer {PARTNER_TOKEN}',
            'Accept': 'application/vnd.yclients.v2+json',
            'Content-Type': 'application/json',
        }, timeout=10)
        data = r.json()
        if data.get('data', {}).get('user_token'):
            _user_token = data['data']['user_token']
            print(f'✅ Auth OK, user_token: {_user_token[:10]}...')
        else:
            print(f'⚠️ Auth failed: {data}')
    except Exception as e:
        print(f'❌ Auth error: {e}')
    return _user_token
 
def headers():
    token = get_user_token()
    auth = f'Bearer {PARTNER_TOKEN}'
    if token:
        auth += f', User {token}'
    return {
        'Authorization': auth,
        'Accept': 'application/vnd.yclients.v2+json',
        'Content-Type': 'application/json',
    }
 
def ycl_get(path, params=None):
    r = requests.get(f'{BASE}{path}', headers=headers(), params=params, timeout=10)
    return r.json()
 
# ── Serve frontend ──────────────────────────────────────────────
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')
 
@app.route('/health')
def health():
    token = get_user_token()
    return jsonify({'status': 'ok', 'salon': SALON_ID, 'auth': bool(token)})
 
# ── API routes ──────────────────────────────────────────────────
@app.route('/api/bookings')
def bookings():
    date = request.args.get('date', '')
    data = ycl_get(f'/records/{SALON_ID}', {
        'start_date': date,
        'end_date': date,
        'count': 200,
        'page': 1,
    })
    return jsonify(data)
 
@app.route('/api/staff')
def staff():
    return jsonify(ycl_get(f'/company/{SALON_ID}/staff'))
 
@app.route('/api/clients')
def clients():
    return jsonify(ycl_get(f'/clients/{SALON_ID}', {
        'count': request.args.get('count', 30),
        'page':  request.args.get('page', 1),
    }))
 
@app.route('/api/analytics')
def analytics():
    date = request.args.get('date', '')
    return jsonify(ycl_get(f'/analytics/finance/{SALON_ID}', {
        'start_date': date, 'end_date': date
    }))
 
@app.route('/api/reviews')
def reviews():
    return jsonify(ycl_get(f'/reviews/{SALON_ID}', {'count': 20}))
 
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8888))
    print(f'\n🔥 Horoshist AI Office → http://localhost:{port}\n')
    get_user_token()
    app.run(host='0.0.0.0', port=port, debug=False)
