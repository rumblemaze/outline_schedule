from flask import Flask, jsonify
from datetime import datetime
import pytz
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import threading
import time

app = Flask(__name__)

# Настройка Google Sheets API
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
try:
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open("Outline Schedule").sheet1  # Замените на имя вашей таблицы
except Exception as e:
    print(f"Ошибка настройки Google Sheets: {e}")
    sheet = None

# Кэш для расписания
schedule_cache = {}
last_updated = 0
UPDATE_INTERVAL = 30  # Секунды

def update_schedule():
    global schedule_cache, last_updated
    while True:
        if sheet:
            try:
                # Чтение данных из Google Таблиц
                data = sheet.get_all_values()
                headers = data[0][1:]  # Сцены (MAIN, SUN, WOODZ, NEON, DARK)
                times = [row[0] for row in data[1:]]  # Временные слоты
                schedule = {"stages": []}
                for col_idx, stage in enumerate(headers, 1):
                    events = []
                    for row_idx, time in enumerate(times):
                        dj = data[row_idx + 1][col_idx]
                        if dj:  # Игнорировать пустые ячейки
                            events.append({"time": time, "dj": dj})
                    schedule["stages"].append({"name": stage, "events": events})
                schedule_cache = schedule
                last_updated = time.time()
            except Exception as e:
                print(f"Ошибка обновления расписания: {e}")
        time.sleep(UPDATE_INTERVAL)

# Запуск фонового обновления
if sheet:
    threading.Thread(target=update_schedule, daemon=True).start()

@app.route('/api/schedule', methods=['GET'])
def get_schedule():
    if not schedule_cache:
        return jsonify({"error": "Расписание недоступно"}), 500
    return jsonify(schedule_cache)

@app.route('/api/timeline', methods=['GET'])
def get_timeline():
    now = datetime.now(pytz.timezone('Europe/Helsinki'))
    start_time = now.replace(hour=19, minute=0, second=0, microsecond=0)
    end_time = now.replace(hour=23, minute=0, second=0, microsecond=0)
    total_minutes = (end_time - start_time).total_seconds() / 60
    elapsed_minutes = (now - start_time).total_seconds() / 60
    if elapsed_minutes < 0 or elapsed_minutes > total_minutes:
        return jsonify({"offset": 0})
    offset = (elapsed_minutes / total_minutes) * 100  # Процент для CSS
    return jsonify({"offset": offset})

@app.route('/')
def index():
    try:
        with open('templates/index.html', 'r') as file:
            return file.read()
    except FileNotFoundError:
        return "Ошибка: index.html не найден", 500

if __name__ == '__main__':
    app.run(debug=True)