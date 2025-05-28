from flask import Flask, jsonify
from datetime import datetime
import pytz
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import threading
import time as time_module
import re
import logging
import os
import json

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__, static_folder='static')

# URL таблицы
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/18h1bFJ1Blj0StrvlJ_sjbR4MgEE9BdUkfDlp6C-e7Ys/edit?gid=0#gid=0"
try:
   SPREADSHEET_ID = re.search(r"/d/([a-zA-Z0-9-_]+)", SPREADSHEET_URL).group(1)
except AttributeError:
   print("Ошибка: Неверный формат URL таблицы")
   SPREADSHEET_ID = None

# Настройка Google Sheets API
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
try:
   # Получение учетных данных из переменной окружения
   credentials_json = os.getenv('GOOGLE_CREDENTIALS')
   if not credentials_json:
       # Если переменная окружения не установлена, пробуем локальный файл
       try:
           with open('credentials.json', 'r') as f:
               creds_dict = json.load(f)
       except FileNotFoundError:
           raise ValueError("Файл credentials.json не найден, и переменная GOOGLE_CREDENTIALS не установлена")
   else:
       creds_dict = json.loads(credentials_json)
   creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
   client = gspread.authorize(creds)
   sheet = client.open_by_key(SPREADSHEET_ID).sheet1 if SPREADSHEET_ID else None
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
               data = sheet.get_all_values()
               headers = data[0][1:]  # Сцены
               times = [row[0] for row in data[1:]]  # Временные слоты
               schedule = {"stages": []}
               for col_idx, stage in enumerate(headers, 1):
                   events = []
                   for row_idx, time in enumerate(times):
                       dj = data[row_idx + 1][col_idx]
                       if dj:
                           events.append({"time": time, "dj": dj})
                   schedule["stages"].append({"name": stage, "events": events})
               schedule_cache = schedule
               last_updated = time_module.time()
               logging.debug("Расписание обновлено: %s", schedule_cache)
           except Exception as e:
               print(f"Ошибка обновления расписания: {e}")
       time_module.sleep(UPDATE_INTERVAL)

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
   offset = (elapsed_minutes / total_minutes) * 100
   return jsonify({"offset": offset})

@app.route('/')
def index():
   try:
       with open('templates/index.html', 'r', encoding='utf-8') as file:
           return file.read()
   except FileNotFoundError:
       return "Ошибка: index.html не найден", 500
   except UnicodeDecodeError:
       return "Ошибка: Неверная кодировка файла index.html", 500

if __name__ == '__main__':
   app.run(debug=False)