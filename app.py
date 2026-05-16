#!/usr/bin/env python3
import os, requests
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder='static')
CORS(app)

PARTNER_TOKEN   = os.environ.get('YCLIENTS_TOKEN', 'l24oXa1Mg26Dw6VW63CE')
SALON_ID        = os.environ.get('SALON_ID', '124859')
LOGIN           = os.environ.get('YCLIENTS_LOGIN', '')
PASSWORD        = os.environ.get('YCLIENTS_PASSWORD', '')
ANTHROPIC_KEY   = os.environ.get('ANTHROPIC_API_KEY', '')
BASE            = 'https://api.yclients.com/api/v1'

_user_token = None

def get_user_token():
    global _user_token
    if _user_token:
        return _user_token
    try:
        r = requests.post(f'{BASE}/auth', json={
            'login': LOGIN, 'password': PASSWORD, 'type': 'user'
        }, headers={
            'Authorization': f'Bearer {PARTNER_TOKEN}',
            'Accept': 'application/vnd.yclients.v2+json',
            'Content-Type': 'application/json',
        }, timeout=10)
        data = r.json()
        if data.get('data', {}).get('user_token'):
            _user_token = data['data']['user_token']
    except Exception as e:
        print(f'Auth error: {e}')
    return _user_token

def ycl_headers():
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
    r = requests.get(f'{BASE}{path}', headers=ycl_headers(), params=params, timeout=10)
    return r.json()

def today():
    from datetime import date
    return date.today().isoformat()

AGENTS = {
    'admin': {
        'name': 'Администратор',
        'prompt': '''Ты — AI-администратор барбершопа Horoshist в Ростове-на-Дону.
Управляешь записями, расписанием мастеров, напоминаниями клиентам.
Отвечай конкретно, на русском языке. Используй данные о записях если они предоставлены.
Будь дружелюбным и профессиональным. Давай практические советы.'''
    },
    'marketer': {
        'name': 'Маркетолог',
        'prompt': '''Ты — AI-маркетолог барбершопа Horoshist в Ростове-на-Дону.
Создаёшь контент для соцсетей, разрабатываешь акции, анализируешь конкурентов.
Пиши живые тексты для Instagram и ВКонтакте. Предлагай готовые посты и идеи.
Отвечай на русском языке. Будь креативным и конкретным.'''
    },
    'analyst': {
        'name': 'Аналитик',
        'prompt': '''Ты — AI-аналитик барбершопа Horoshist в Ростове-на-Дону.
Анализируешь выручку, загрузку мастеров, средний чек, прогнозы.
Работаешь с реальными данными из YClients. Давай конкретные цифры и рекомендации.
Отвечай на русском языке. Будь точным и аналитичным.'''
    },
    'reputation': {
        'name': 'Репутация',
        'prompt': '''Ты — AI-агент репутации барбершопа Horoshist в Ростове-на-Дону.
Работаешь с отзывами, повышаешь NPS, управляешь лояльностью клиентов.
Пишешь вежливые персональные ответы на отзывы. Анализируешь обратную связь.
Отвечай на русском языке. Будь тактичным и клиентоориентированным.'''
    }
}

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'salon': SALON_ID, 'ai': bool(ANTHROPIC_KEY)})

@app.route('/api/bookings')
def bookings():
    date = request.args.get('date', today())
    data = ycl_get(f'/records/{SALON_ID}', {
        'start_date': date, 'end_date': date, 'count': 200, 'page': 1,
    })
    return jsonify(data)

@app.route('/api/staff')
def staff():
    return jsonify(ycl_get(f'/company/{SALON_ID}/staff'))

@app.route('/api/clients')
def clients():
    return jsonify(ycl_get(f'/clients/{SALON_ID}', {
        'count': request.args.get('count', 30),
        'page': request.args.get('page', 1),
    }))

@app.route('/api/analytics')
def analytics():
    date = request.args.get('date', today())
    return jsonify(ycl_get(f'/analytics/finance/{SALON_ID}', {
        'start_date': date, 'end_date': date
    }))

@app.route('/api/reviews')
def reviews():
    return jsonify(ycl_get(f'/reviews/{SALON_ID}', {'count': 20}))

@app.route('/api/agent', methods=['POST'])
def agent():
    if not ANTHROPIC_KEY:
        return jsonify({'error': 'ANTHROPIC_API_KEY не настроен'}), 500

    body     = request.json or {}
    agent_id = body.get('agent', 'admin')
    message  = body.get('message', '')
    history  = body.get('history', [])
    ag       = AGENTS.get(agent_id, AGENTS['admin'])

    # Get live YClients context
    context = ''
    try:
        books = ycl_get(f'/records/{SALON_ID}', {
            'start_date': today(), 'end_date': today(), 'count': 200, 'page': 1
        })
        recs = books.get('data', [])
        if recs:
            from datetime import datetime
            now = datetime.now()
            active = [r for r in recs if not r.get('deleted')]
            future = sorted(
                [r for r in active if datetime.fromisoformat(r['datetime'][:19]) > now],
                key=lambda x: x['datetime']
            )
            context = f'\n\n[Живые данные YClients на {today()}]'
            context += f'\n- Всего записей сегодня: {len(active)}'
            context += f'\n- Предстоящих: {len(future)}'
            if future:
                nb = future[0]
                context += f'\n- Ближайшая: {nb["datetime"][11:16]} — {nb.get("client",{}).get("name","Клиент")}, {nb.get("services",[{}])[0].get("title","услуга")}, мастер: {nb.get("staff",{}).get("name","—")}'
            # Staff count
            staff_data = ycl_get(f'/company/{SALON_ID}/staff')
            staff_list = [s for s in (staff_data.get('data') or []) if not s.get('fired')]
            context += f'\n- Мастеров активных: {len(staff_list)}'
    except Exception as e:
        context = f'\n[Данные YClients: ошибка — {e}]'

    system = ag['prompt'] + context

    messages = []
    for h in (history or [])[-10:]:
        messages.append({'role': h['role'], 'content': h['content']})
    messages.append({'role': 'user', 'content': message})

    try:
        r = requests.post('https://api.anthropic.com/v1/messages', json={
            'model': 'claude-haiku-4-5-20251001',
            'max_tokens': 1024,
            'system': system,
            'messages': messages,
        }, headers={
            'x-api-key': ANTHROPIC_KEY,
            'anthropic-version': '2023-06-01',
            'content-type': 'application/json',
        }, timeout=30)

        data = r.json()
        if 'content' in data:
            return jsonify({'reply': data['content'][0]['text'], 'agent': ag['name']})
        else:
            return jsonify({'error': str(data)}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8888))
    print(f'\n🔥 Horoshist AI Office → http://localhost:{port}')
    get_user_token()
    app.run(host='0.0.0.0', port=port, debug=False)
