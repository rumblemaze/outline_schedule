# Создание приложения для музыкального фестиваля
_Exported on 6/4/2025 at 22:59:01 GMT+3 from Cursor (0.50.5)_

---

**User**

Я хочу написать приложение в телеграме или айфоне (не знаю как это технически реализовать, я пишу тока на питоне) для фестиваля музыки.
Обычно все пользуются вот таким пдф-файлом с расписанием, и это не очень удобно. Я хочу чтобы в приложении была бегущая сверху вниз строка согласно актуальному времени, и указывала на то, где какой диджей играет. При этом визуально расписание можно будет приближать и отдалять так как если бы это были карты (имею ввиду то, что размер текста остается статичен). Условно я могу зазумить в сцену Woodz и увидеть таблицу со временем и диджеями

Отвечай на русском

Сейчас эта хуйня ничего не отображает и не работает

---

**Cursor**

Я понимаю вашу задачу. Давайте создадим интерактивное приложение для расписания музыкального фестиваля. Для начала я посмотрю, что у нас есть в проекте.


Давайте посмотрим содержимое основных файлов, чтобы понять текущую реализацию.


Я вижу, что у вас уже есть базовая структура приложения на Flask с JSON-файлом расписания. Давайте улучшим его, добавив интерактивный интерфейс с бегущей строкой и возможностью зума.

Для этого нам нужно:
1. Создать современный веб-интерфейс с использованием HTML5, CSS и JavaScript
2. Добавить интерактивную временную шкалу
3. Реализовать функционал зума для разных сцен

Сначала создадим новый HTML-шаблон:


```html
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Расписание фестиваля</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Roboto', sans-serif;
            background: #1a1a1a;
            color: #ffffff;
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        .timeline-container {
            position: relative;
            margin: 20px 0;
            overflow: hidden;
        }

        .current-time-marker {
            position: absolute;
            left: 0;
            width: 2px;
            height: 100%;
            background: #ff3e3e;
            z-index: 1000;
            transition: left 0.5s ease;
        }

        .stages {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }

        .stage {
            background: #2a2a2a;
            border-radius: 10px;
            padding: 20px;
            transition: transform 0.3s ease;
        }

        .stage-header {
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 15px;
            color: #ff3e3e;
        }

        .events {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }

        .event {
            background: #333;
            padding: 15px;
            border-radius: 8px;
            transition: transform 0.2s ease;
        }

        .event:hover {
            transform: scale(1.05);
        }

        .event-time {
            font-size: 18px;
            color: #ff3e3e;
            margin-bottom: 5px;
        }

        .event-dj {
            font-size: 16px;
        }

        .controls {
            position: fixed;
            bottom: 20px;
            right: 20px;
            display: flex;
            gap: 10px;
            background: rgba(42, 42, 42, 0.9);
            padding: 10px;
            border-radius: 10px;
            z-index: 1000;
        }

        .zoom-btn {
            background: #ff3e3e;
            border: none;
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            transition: background 0.2s ease;
        }

        .zoom-btn:hover {
            background: #ff5252;
        }

        .current-stage {
            transform: scale(1.1);
            box-shadow: 0 0 20px rgba(255, 62, 62, 0.3);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="timeline-container">
            <div class="current-time-marker"></div>
            <div class="stages" id="stages"></div>
        </div>
    </div>
    <div class="controls">
        <button class="zoom-btn" onclick="zoomIn()">+</button>
        <button class="zoom-btn" onclick="zoomOut()">-</button>
    </div>

    <script>
        let currentZoom = 1;
        const ZOOM_STEP = 0.1;
        const MAX_ZOOM = 2;
        const MIN_ZOOM = 0.5;

        function updateCurrentTimeMarker() {
            fetch('/api/timeline')
                .then(response => response.json())
                .then(data => {
                    const marker = document.querySelector('.current-time-marker');
                    marker.style.left = `${data.offset}%`;
                });
        }

        function updateSchedule() {
            fetch('/api/schedule')
                .then(response => response.json())
                .then(data => {
                    const stagesContainer = document.getElementById('stages');
                    stagesContainer.innerHTML = '';

                    data.stages.forEach(stage => {
                        const stageElement = document.createElement('div');
                        stageElement.className = 'stage';
                        stageElement.innerHTML = `
                            <div class="stage-header">${stage.name}</div>
                            <div class="events">
                                ${stage.events.map(event => `
                                    <div class="event">
                                        <div class="event-time">${event.time}</div>
                                        <div class="event-dj">${event.dj}</div>
                                    </div>
                                `).join('')}
                            </div>
                        `;
                        stagesContainer.appendChild(stageElement);
                    });

                    highlightCurrentStage();
                });
        }

        function highlightCurrentStage() {
            const now = new Date();
            const currentHour = now.getHours();
            const currentMinute = now.getMinutes();
            const currentTime = currentHour + currentMinute / 60;

            const stages = document.querySelectorAll('.stage');
            stages.forEach(stage => {
                const events = stage.querySelectorAll('.event');
                let isCurrentStage = false;

                events.forEach(event => {
                    const timeText = event.querySelector('.event-time').textContent;
                    const [hours, minutes] = timeText.split(':').map(Number);
                    const eventTime = hours + minutes / 60;

                    if (Math.abs(eventTime - currentTime) < 1) {
                        isCurrentStage = true;
                    }
                });

                stage.classList.toggle('current-stage', isCurrentStage);
            });
        }

        function zoomIn() {
            if (currentZoom < MAX_ZOOM) {
                currentZoom += ZOOM_STEP;
                updateZoom();
            }
        }

        function zoomOut() {
            if (currentZoom > MIN_ZOOM) {
                currentZoom -= ZOOM_STEP;
                updateZoom();
            }
        }

        function updateZoom() {
            const stages = document.querySelector('.stages');
            stages.style.transform = `scale(${currentZoom})`;
        }

        // Обновляем данные каждую минуту
        setInterval(() => {
            updateCurrentTimeMarker();
            updateSchedule();
        }, 60000);

        // Инициализация
        updateCurrentTimeMarker();
        updateSchedule();
    </script>
</body>
</html>
```

Теперь давайте обновим бэкенд, чтобы он корректно работал с новым интерфейсом:


```python
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
```

Теперь давайте обновим файл с зависимостями:


```plaintext
flask==3.0.2
pytz==2024.1
python-dotenv==1.0.1
```

Отлично! Я создал современное веб-приложение для расписания фестиваля. Вот что оно умеет:

1. Показывает расписание всех сцен в виде карточек
2. Имеет бегущую красную линию, которая показывает текущее время
3. Подсвечивает текущую сцену (где сейчас идет выступление)
4. Позволяет увеличивать и уменьшать масштаб с помощью кнопок + и -
5. Автоматически обновляет данные каждую минуту
6. Имеет современный темный дизайн с анимациями

Чтобы запустить приложение:

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Запустите сервер:
```bash
python festival_schedule_app.py
```

3. Откройте в браузере: http://localhost:5000

Приложение будет доступно на всех устройствах в вашей локальной сети по IP-адресу компьютера.

Вы можете легко обновлять расписание, редактируя файл `schedule.json`. Формат данных остался прежним.

Хотите ли вы что-то изменить или добавить в приложение?

```shellscript
pip install -r requirements.txt
```

```shellscript
python festival_schedule_app.py
```

---

**User**

Бля это уже в тыщу раз круче чем я делал до этого. Давай работать. Для начала я хочу изменить порядок - сцена должна быть колонкой, а время - строкой. Диджеи в своих клетках должны двигаться свободно при свайпах в любые стороны, а колонки времени и сцен должны быть зафискированы, но так, чтобы елозить (время может двигаться вверх-вниз, а сцены влево-вправо). Таким образом всегда будет визуально видно время и сцену. Вообще расписание будет заполнено в течение четырех дней, поэтому можешь сгенерировать рандомные названия и время для теста в schedule.json. 

Напоминаю что при этом сверху вниз должна быть бегущая строка которая указывает на текущее время по всей таблице (опять же чтобы визуально видетьь что сейчас играет)

---

**Cursor**

Понял вашу задачу. Давайте сначала обновим структуру данных в `schedule.json` с тестовыми данными на 4 дня:


```json
{
    "stages": [
        {
            "name": "MAIN",
            "events": [
                {"time": "2024-05-30 12:00", "dj": "Cosmic Voyager"},
                {"time": "2024-05-30 14:00", "dj": "Neon Pulse"},
                {"time": "2024-05-30 16:00", "dj": "Digital Dreamer"},
                {"time": "2024-05-30 18:00", "dj": "Echo Wave"},
                {"time": "2024-05-30 20:00", "dj": "Midnight Rider"},
                {"time": "2024-05-30 22:00", "dj": "Stellar Beats"},
                {"time": "2024-05-31 12:00", "dj": "Quantum Flux"},
                {"time": "2024-05-31 14:00", "dj": "Solar Wind"},
                {"time": "2024-05-31 16:00", "dj": "Lunar Phase"},
                {"time": "2024-05-31 18:00", "dj": "Cosmic Dust"},
                {"time": "2024-05-31 20:00", "dj": "Nebula Sound"},
                {"time": "2024-05-31 22:00", "dj": "Galactic Pulse"},
                {"time": "2024-06-01 12:00", "dj": "Star Child"},
                {"time": "2024-06-01 14:00", "dj": "Moon Walker"},
                {"time": "2024-06-01 16:00", "dj": "Sun Seeker"},
                {"time": "2024-06-01 18:00", "dj": "Earth Shaker"},
                {"time": "2024-06-01 20:00", "dj": "Mars Rover"},
                {"time": "2024-06-01 22:00", "dj": "Jupiter Jump"},
                {"time": "2024-06-02 12:00", "dj": "Saturn Rings"},
                {"time": "2024-06-02 14:00", "dj": "Uranus Flow"},
                {"time": "2024-06-02 16:00", "dj": "Neptune Wave"},
                {"time": "2024-06-02 18:00", "dj": "Pluto Beat"},
                {"time": "2024-06-02 20:00", "dj": "Mercury Rising"},
                {"time": "2024-06-02 22:00", "dj": "Venus Fly"}
            ]
        },
        {
            "name": "WOODZ",
            "events": [
                {"time": "2024-05-30 12:00", "dj": "Forest Spirit"},
                {"time": "2024-05-30 14:00", "dj": "Woodland Echo"},
                {"time": "2024-05-30 16:00", "dj": "Pine Groove"},
                {"time": "2024-05-30 18:00", "dj": "Oak Rhythm"},
                {"time": "2024-05-30 20:00", "dj": "Maple Beat"},
                {"time": "2024-05-30 22:00", "dj": "Birch Bass"},
                {"time": "2024-05-31 12:00", "dj": "Cedar Sound"},
                {"time": "2024-05-31 14:00", "dj": "Elm Wave"},
                {"time": "2024-05-31 16:00", "dj": "Ash Flow"},
                {"time": "2024-05-31 18:00", "dj": "Beech Beat"},
                {"time": "2024-05-31 20:00", "dj": "Chestnut Groove"},
                {"time": "2024-05-31 22:00", "dj": "Walnut Bass"},
                {"time": "2024-06-01 12:00", "dj": "Pineapple Beat"},
                {"time": "2024-06-01 14:00", "dj": "Coconut Flow"},
                {"time": "2024-06-01 16:00", "dj": "Banana Groove"},
                {"time": "2024-06-01 18:00", "dj": "Mango Bass"},
                {"time": "2024-06-01 20:00", "dj": "Kiwi Sound"},
                {"time": "2024-06-01 22:00", "dj": "Peach Wave"},
                {"time": "2024-06-02 12:00", "dj": "Apple Beat"},
                {"time": "2024-06-02 14:00", "dj": "Pear Flow"},
                {"time": "2024-06-02 16:00", "dj": "Plum Groove"},
                {"time": "2024-06-02 18:00", "dj": "Cherry Bass"},
                {"time": "2024-06-02 20:00", "dj": "Berry Sound"},
                {"time": "2024-06-02 22:00", "dj": "Grape Wave"}
            ]
        },
        {
            "name": "NEON",
            "events": [
                {"time": "2024-05-30 12:00", "dj": "Neon Lights"},
                {"time": "2024-05-30 14:00", "dj": "Glow Master"},
                {"time": "2024-05-30 16:00", "dj": "Bright Future"},
                {"time": "2024-05-30 18:00", "dj": "Shine On"},
                {"time": "2024-05-30 20:00", "dj": "Light Wave"},
                {"time": "2024-05-30 22:00", "dj": "Spark Beat"},
                {"time": "2024-05-31 12:00", "dj": "Flash Point"},
                {"time": "2024-05-31 14:00", "dj": "Beam Rider"},
                {"time": "2024-05-31 16:00", "dj": "Ray Master"},
                {"time": "2024-05-31 18:00", "dj": "Photon Flow"},
                {"time": "2024-05-31 20:00", "dj": "Laser Beat"},
                {"time": "2024-05-31 22:00", "dj": "Quantum Light"},
                {"time": "2024-06-01 12:00", "dj": "Solar Flare"},
                {"time": "2024-06-01 14:00", "dj": "Lunar Glow"},
                {"time": "2024-06-01 16:00", "dj": "Stellar Light"},
                {"time": "2024-06-01 18:00", "dj": "Cosmic Ray"},
                {"time": "2024-06-01 20:00", "dj": "Galactic Beam"},
                {"time": "2024-06-01 22:00", "dj": "Nebula Flash"},
                {"time": "2024-06-02 12:00", "dj": "Star Light"},
                {"time": "2024-06-02 14:00", "dj": "Moon Beam"},
                {"time": "2024-06-02 16:00", "dj": "Sun Ray"},
                {"time": "2024-06-02 18:00", "dj": "Earth Light"},
                {"time": "2024-06-02 20:00", "dj": "Mars Glow"},
                {"time": "2024-06-02 22:00", "dj": "Jupiter Flash"}
            ]
        },
        {
            "name": "DARK",
            "events": [
                {"time": "2024-05-30 12:00", "dj": "Shadow Master"},
                {"time": "2024-05-30 14:00", "dj": "Dark Matter"},
                {"time": "2024-05-30 16:00", "dj": "Black Hole"},
                {"time": "2024-05-30 18:00", "dj": "Night Rider"},
                {"time": "2024-05-30 20:00", "dj": "Midnight Flow"},
                {"time": "2024-05-30 22:00", "dj": "Dark Beat"},
                {"time": "2024-05-31 12:00", "dj": "Shadow Wave"},
                {"time": "2024-05-31 14:00", "dj": "Dark Pulse"},
                {"time": "2024-05-31 16:00", "dj": "Black Light"},
                {"time": "2024-05-31 18:00", "dj": "Night Sound"},
                {"time": "2024-05-31 20:00", "dj": "Midnight Groove"},
                {"time": "2024-05-31 22:00", "dj": "Dark Bass"},
                {"time": "2024-06-01 12:00", "dj": "Shadow Flow"},
                {"time": "2024-06-01 14:00", "dj": "Dark Wave"},
                {"time": "2024-06-01 16:00", "dj": "Black Beat"},
                {"time": "2024-06-01 18:00", "dj": "Night Light"},
                {"time": "2024-06-01 20:00", "dj": "Midnight Sound"},
                {"time": "2024-06-01 22:00", "dj": "Dark Groove"},
                {"time": "2024-06-02 12:00", "dj": "Shadow Bass"},
                {"time": "2024-06-02 14:00", "dj": "Dark Flow"},
                {"time": "2024-06-02 16:00", "dj": "Black Wave"},
                {"time": "2024-06-02 18:00", "dj": "Night Beat"},
                {"time": "2024-06-02 20:00", "dj": "Midnight Light"},
                {"time": "2024-06-02 22:00", "dj": "Dark Sound"}
            ]
        }
    ]
}
```

Теперь давайте обновим интерфейс, чтобы реализовать новую структуру с фиксированными колонками и строками:


```html
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Расписание фестиваля</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Roboto', sans-serif;
            background: #1a1a1a;
            color: #ffffff;
            min-height: 100vh;
            overflow: hidden;
        }

        .schedule-container {
            position: relative;
            width: 100vw;
            height: 100vh;
            overflow: hidden;
        }

        .time-column {
            position: fixed;
            left: 0;
            top: 0;
            width: 80px;
            height: 100vh;
            background: #2a2a2a;
            z-index: 100;
            overflow-y: auto;
            scrollbar-width: none;
        }

        .time-column::-webkit-scrollbar {
            display: none;
        }

        .time-slot {
            height: 100px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
            color: #ff3e3e;
            border-bottom: 1px solid #333;
        }

        .stages-container {
            position: absolute;
            left: 80px;
            top: 0;
            right: 0;
            height: 100vh;
            overflow: auto;
        }

        .stages-header {
            position: fixed;
            top: 0;
            left: 80px;
            right: 0;
            height: 60px;
            background: #2a2a2a;
            z-index: 90;
            display: flex;
            overflow-x: auto;
            scrollbar-width: none;
        }

        .stages-header::-webkit-scrollbar {
            display: none;
        }

        .stage-header {
            min-width: 200px;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            font-weight: 700;
            color: #ff3e3e;
            border-right: 1px solid #333;
            padding: 0 20px;
            white-space: nowrap;
        }

        .schedule-grid {
            position: absolute;
            top: 60px;
            left: 0;
            right: 0;
            display: flex;
        }

        .stage-column {
            min-width: 200px;
            border-right: 1px solid #333;
        }

        .event-slot {
            height: 100px;
            border-bottom: 1px solid #333;
            padding: 10px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            background: #333;
            transition: transform 0.2s ease;
        }

        .event-slot:hover {
            transform: scale(1.05);
            z-index: 10;
        }

        .event-dj {
            font-size: 14px;
            margin-top: 5px;
        }

        .current-time-marker {
            position: fixed;
            left: 0;
            width: 100%;
            height: 2px;
            background: #ff3e3e;
            z-index: 1000;
            pointer-events: none;
            transition: top 0.5s ease;
        }

        .controls {
            position: fixed;
            bottom: 20px;
            right: 20px;
            display: flex;
            gap: 10px;
            background: rgba(42, 42, 42, 0.9);
            padding: 10px;
            border-radius: 10px;
            z-index: 1000;
        }

        .zoom-btn {
            background: #ff3e3e;
            border: none;
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            transition: background 0.2s ease;
        }

        .zoom-btn:hover {
            background: #ff5252;
        }

        .current-event {
            background: #ff3e3e20;
            border: 1px solid #ff3e3e;
        }
    </style>
</head>
<body>
    <div class="schedule-container">
        <div class="time-column" id="timeColumn"></div>
        <div class="stages-container">
            <div class="stages-header" id="stagesHeader"></div>
            <div class="schedule-grid" id="scheduleGrid"></div>
        </div>
        <div class="current-time-marker" id="currentTimeMarker"></div>
        <div class="controls">
            <button class="zoom-btn" onclick="zoomIn()">+</button>
            <button class="zoom-btn" onclick="zoomOut()">-</button>
        </div>
    </div>

    <script>
        let currentZoom = 1;
        const ZOOM_STEP = 0.1;
        const MAX_ZOOM = 2;
        const MIN_ZOOM = 0.5;
        let scheduleData = null;

        function formatTime(timeStr) {
            const date = new Date(timeStr);
            return date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
        }

        function formatDate(timeStr) {
            const date = new Date(timeStr);
            return date.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit' });
        }

        function updateCurrentTimeMarker() {
            fetch('/api/timeline')
                .then(response => response.json())
                .then(data => {
                    const marker = document.getElementById('currentTimeMarker');
                    marker.style.top = `${data.offset}%`;
                });
        }

        function updateSchedule() {
            fetch('/api/schedule')
                .then(response => response.json())
                .then(data => {
                    scheduleData = data;
                    renderSchedule();
                });
        }

        function renderSchedule() {
            if (!scheduleData) return;

            // Получаем все уникальные времена
            const times = new Set();
            scheduleData.stages.forEach(stage => {
                stage.events.forEach(event => {
                    times.add(event.time);
                });
            });
            const sortedTimes = Array.from(times).sort();

            // Рендерим колонку времени
            const timeColumn = document.getElementById('timeColumn');
            timeColumn.innerHTML = sortedTimes.map(time => `
                <div class="time-slot">
                    <div>
                        <div>${formatTime(time)}</div>
                        <div style="font-size: 10px; color: #666;">${formatDate(time)}</div>
                    </div>
                </div>
            `).join('');

            // Рендерим заголовки сцен
            const stagesHeader = document.getElementById('stagesHeader');
            stagesHeader.innerHTML = scheduleData.stages.map(stage => `
                <div class="stage-header">${stage.name}</div>
            `).join('');

            // Рендерим сетку расписания
            const scheduleGrid = document.getElementById('scheduleGrid');
            scheduleGrid.innerHTML = scheduleData.stages.map(stage => `
                <div class="stage-column">
                    ${sortedTimes.map(time => {
                        const event = stage.events.find(e => e.time === time);
                        return `
                            <div class="event-slot" data-time="${time}">
                                ${event ? `
                                    <div class="event-dj">${event.dj}</div>
                                ` : ''}
                            </div>
                        `;
                    }).join('')}
                </div>
            `).join('');

            highlightCurrentEvents();
        }

        function highlightCurrentEvents() {
            const now = new Date();
            const currentTime = now.toISOString().slice(0, 16); // YYYY-MM-DDTHH:mm

            document.querySelectorAll('.event-slot').forEach(slot => {
                const slotTime = slot.dataset.time;
                const slotDate = new Date(slotTime);
                const timeDiff = Math.abs(slotDate - now) / (1000 * 60); // разница в минутах

                slot.classList.toggle('current-event', timeDiff < 60); // подсвечиваем события в течение часа
            });
        }

        function zoomIn() {
            if (currentZoom < MAX_ZOOM) {
                currentZoom += ZOOM_STEP;
                updateZoom();
            }
        }

        function zoomOut() {
            if (currentZoom > MIN_ZOOM) {
                currentZoom -= ZOOM_STEP;
                updateZoom();
            }
        }

        function updateZoom() {
            const scheduleGrid = document.getElementById('scheduleGrid');
            scheduleGrid.style.transform = `scale(${currentZoom})`;
            scheduleGrid.style.transformOrigin = 'top left';
        }

        // Синхронизация скролла
        const timeColumn = document.getElementById('timeColumn');
        const stagesContainer = document.querySelector('.stages-container');

        timeColumn.addEventListener('scroll', () => {
            stagesContainer.scrollTop = timeColumn.scrollTop;
        });

        stagesContainer.addEventListener('scroll', () => {
            timeColumn.scrollTop = stagesContainer.scrollTop;
        });

        // Обновляем данные каждую минуту
        setInterval(() => {
            updateCurrentTimeMarker();
            updateSchedule();
        }, 60000);

        // Инициализация
        updateCurrentTimeMarker();
        updateSchedule();
    </script>
</body>
</html>
```

Теперь давайте обновим бэкенд для работы с новым форматом времени:


```python
from flask import Flask, jsonify, send_from_directory
from datetime import datetime, timedelta
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
    
    # Находим ближайшее время в расписании
    min_time = None
    max_time = None
    
    for stage in schedule_cache.get('stages', []):
        for event in stage.get('events', []):
            event_time = datetime.strptime(event['time'], '%Y-%m-%d %H:%M')
            if min_time is None or event_time < min_time:
                min_time = event_time
            if max_time is None or event_time > max_time:
                max_time = event_time
    
    if min_time is None or max_time is None:
        return jsonify({"offset": 0})
    
    # Вычисляем смещение текущего времени
    total_duration = (max_time - min_time).total_seconds()
    if total_duration == 0:
        return jsonify({"offset": 0})
    
    current_offset = (now - min_time).total_seconds() / total_duration
    current_offset = max(0, min(1, current_offset))  # Ограничиваем значения от 0 до 1
    
    return jsonify({"offset": current_offset * 100})

@app.route('/')
def index():
    return send_from_directory('templates', 'index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

Я полностью переработал интерфейс и бэкенд согласно вашим требованиям. Теперь:

1. Время отображается в левой колонке и фиксировано
2. Названия сцен отображаются в верхней строке и фиксированы
3. Основная сетка с диджеями можно прокручивать в любом направлении
4. Бегущая красная линия показывает текущее время
5. Текущие выступления подсвечиваются красным
6. Можно увеличивать и уменьшать масштаб
7. Добавлены даты для каждого временного слота
8. Синхронизирован скролл между временной колонкой и основной сеткой

Чтобы запустить приложение:

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Запустите сервер:
```bash
python festival_schedule_app.py
```

3. Откройте в браузере: http://localhost:5000

Теперь вы можете:
- Прокручивать время вверх-вниз
- Прокручивать сцены влево-вправо
- Увеличивать/уменьшать масштаб
- Видеть текущее время по красной линии
- Видеть текущие выступления по подсветке

Хотите что-то изменить или добавить?

```shellscript
pip install -r requirements.txt
```

```shellscript
python festival_schedule_app.py
```

