# Horoshist AI Office 🔥

AI-дашборд для управления барбершопом — подключён к YClients API в реальном времени.

## Деплой на Render.com (бесплатно, 3 минуты)

### Шаг 1 — Загрузи на GitHub
1. Зайди на [github.com](https://github.com) → войди или зарегистрируйся
2. Нажми **"New repository"** → назови `horoshist-ai-office`
3. Нажми **"Create repository"**
4. Загрузи все 4 файла из этой папки:
   - `app.py`
   - `requirements.txt`
   - `render.yaml`
   - папку `static/` с файлом `index.html`

### Шаг 2 — Подключи к Render
1. Зайди на [render.com](https://render.com) → **Sign up with GitHub**
2. Нажми **"New +"** → **"Web Service"**
3. Выбери репозиторий `horoshist-ai-office`
4. Render сам определит настройки из `render.yaml`
5. Нажми **"Create Web Service"**
6. Подожди ~2 минуты пока задеплоится

### Шаг 3 — Готово!
Render даст ссылку вида `https://horoshist-ai-office.onrender.com`
Это и есть твой живой дашборд — открывай с любого устройства!

## Что умеет дашборд
- 📅 Живые записи из YClients (обновление каждую минуту)
- 👥 Клиентская база
- 👨‍💼 Команда мастеров
- 💰 Аналитика выручки
- ⭐ Отзывы клиентов
- 🤖 AI-агенты с задачами

## Переменные окружения (уже в render.yaml)
- `YCLIENTS_TOKEN` — токен партнёра YClients
- `SALON_ID` — ID филиала (124859)

> ⚠️ После деплоя смени токен в настройках YClients и обнови его в Render → Environment
