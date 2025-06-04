from flask import Flask, jsonify, send_from_directory
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
    now = datetime.now(pytz.timezone('Europe/Moscow'))
    current_time = now.hour + now.minute / 60
    
    # Находим ближайшее время в расписании
    min_time = float('inf')
    max_time = float('-inf')
    
    for stage in schedule_cache.get('stages', []):
        for event in stage.get('events', []):
            time_str = event.get('time', '')
            if time_str:
                hours, minutes = map(int, time_str.split(':'))
                event_time = hours + minutes / 60
                min_time = min(min_time, event_time)
                max_time = max(max_time, event_time)
    
    if min_time == float('inf') or max_time == float('-inf'):
        return jsonify({"offset": 0})
    
    # Вычисляем смещение текущего времени
    total_duration = max_time - min_time
    if total_duration == 0:
        return jsonify({"offset": 0})
    
    current_offset = (current_time - min_time) / total_duration
    current_offset = max(0, min(1, current_offset))  # Ограничиваем значения от 0 до 1
    
    return jsonify({"offset": current_offset * 100})

@app.route('/')
def index():
    return send_from_directory('templates', 'index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)