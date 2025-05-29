from flask import Flask, jsonify
from datetime import datetime
import pytz
import logging
import os
import json
import threading
import time as time_module

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__, static_folder='static')

# Кэш для расписания
schedule_cache = {}
last_updated = 0
UPDATE_INTERVAL = 30  # Секунды

def load_schedule():
    global schedule_cache, last_updated
    try:
        schedule_path = os.path.join(os.path.dirname(__file__), 'schedule.json')
        logging.debug(f"Попытка загрузки schedule.json по пути: {schedule_path}")
        with open(schedule_path, 'r', encoding='utf-8') as f:
            schedule_cache = json.load(f)
        last_updated = time_module.time()
        logging.debug("Расписание успешно загружено из schedule.json: %s", schedule_cache)
    except Exception as e:
        logging.error(f"Ошибка загрузки расписания из JSON: {e}")
        schedule_cache = {"error": f"Ошибка загрузки расписания: {str(e)}"}

def update_schedule():
    global schedule_cache, last_updated
    while True:
        load_schedule()
        time_module.sleep(UPDATE_INTERVAL)

# Загружаем расписание синхронно при старте
load_schedule()

# Запускаем фоновую загрузку
threading.Thread(target=update_schedule, daemon=True).start()

@app.route('/api/schedule', methods=['GET'])
def get_schedule():
    if not schedule_cache or "error" in schedule_cache:
        logging.error(f"Ошибка в get_schedule: schedule_cache недоступен: {schedule_cache}")
        return jsonify({"error": "Расписание недоступно"}), 500
    logging.debug(f"Возвращаем schedule_cache: {schedule_cache}")
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
    offset = (elapsed_minutes / total_minutes) * 100
    return jsonify({"offset": offset})

@app.route('/')
def index():
    try:
        index_path = os.path.join(os.path.dirname(__file__), 'templates', 'index.html')
        with open(index_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        directories = [d for d in os.listdir(os.path.dirname(__file__)) if os.path.isdir(d)]
        return f"Ошибка: index.html не найден. Доступные директории: {', '.join(directories)}", 500
    except UnicodeDecodeError:
        return "Ошибка: Неверная кодировка файла index.html", 500

if __name__ == '__main__':
    app.run(debug=False)